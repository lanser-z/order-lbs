import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, HTTPError
import redis, hashlib
import sys, os.path, json, logging.config, datetime

# locate base dir
base_dir = sys.path[0]
if os.path.isfile(base_dir):
    base_dir = os.path.dirname(base_dir)

# define logger
logging.config.fileConfig(os.path.join(base_dir, 'logging.conf'))
logger = logging.getLogger('root')
LOG_DEBUG = logger.debug
LOG_INFO = logger.info
LOG_WARN = logger.warning
LOG_ERROR = logger.error

# connect redis
try:
    mc = redis.Redis('127.0.0.1', 6379)
    # mc = redis.Redis('192.168.2.108', 6379)
    assert isinstance(mc, redis.Redis)
except Exception as e:
    LOG_ERROR('connect redis failed %s' % e)
    sys.exit(1)

# define consts
ROLE_SALER = 'saler'
ROLE_CUSTOMER = 'customer'
ROLES = (ROLE_SALER, ROLE_CUSTOMER)
TEMPLATE_MARK = 'RENDER_NAME'

# define model
class Shop:
    ID = 'id'
    @staticmethod
    def GenShopKey(shop, role):
        if role in ROLES:
            m = hashlib.md5()
            m.update(f'{shop}-{role}'.encode("utf8"))
            m.update('monty-python-salt'.encode("utf8")) # 防撞码攻击
            return m.hexdigest()
        else:
            return None

    @staticmethod
    def NewShop(shop):
        if mc.exists(*list(map(lambda r: Shop.GenShopKey(shop, r), ROLES))):
            LOG_WARN(f'new shop {shop} faild, exists')
            return False
        else:
            for role in ROLES:
                mc.set(Shop.GenShopKey(shop, role), shop)
            mc.set(f'{shop}-{Shop.ID}', 0)
            LOG_INFO(f'new shop {shop} done')
            return True

    @staticmethod
    def DelShop(shop):
        if not mc.exists(*list(map(lambda r: Shop.GenShopKey(shop, r), ROLES))):
            LOG_WARN(f'delete shop {shop} faild, not exists')
            return False
        for role in ROLES:
            mc.delete(Shop.GenShopKey(shop, role), shop)
        shopOrderCount = Shop.GetShopOrderCount(shop)
        for i in range(1, shopOrderCount+1):
            entry = f'{shop}-{i}'
            mc.hdel(entry, *mc.hkeys(entry))
        LOG_INFO(f'delete shop {shop} done')
        return True

    @staticmethod
    def GetNameByKey(shopKey):
        return mc.get(shopKey).decode('utf8')

    @staticmethod
    def GetShopOrderCount(shop):
        shopOrderCount = mc.get(f'{shop}-{Shop.ID}')
        return int(shopOrderCount)

    @staticmethod
    def Valid(shop, role):
        return mc.exists(shop) and role in ROLES

    def __init__(self, shopKey, role):
        self.shop = Shop.GetNameByKey(shopKey)
        self.role = role

    def __NewId(self):
        return str(mc.incr(f'{self.shop}-{Shop.ID}'))

    def __CurrentTime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __FillOrder(self, data, role, id):
        order = {}
        if role == ROLE_CUSTOMER and int(data[b'stat']) in (0, 1):
            order['time'] = data[b'time'].decode('utf8')
            name = data[b'name'].decode('utf8')
            order['name'] = name[0] + (len(name) - 1) * '*'
            telephone = data[b'telephone'].decode('utf8')
            order['telephone'] = telephone[:3] + (len(telephone)-6) * '*' + telephone[-3:]
            order['address'] = data[b'address'].decode('utf8')
        elif role == ROLE_SALER:
            order['id'] = id
            order['time'] = data[b'time'].decode('utf8')
            order['name'] = data[b'name'].decode('utf8')
            order['telephone'] = data[b'telephone'].decode('utf8')
            order['address'] = data[b'address'].decode('utf8')
            order['items'] = data[b'items'].decode('utf8')
            order['note'] = data[b'note'].decode('utf8')
            order['stat'] = int(data[b'stat'])
            if b'point' in data:
                order['point'] = data[b'point'].decode('utf8')
        return order

    def IsValid(self):
        return self.Valid(self.GenShopKey(self.shop, self.role), self.role)

    def NewOrder(self, name, address, telephone, items, note, lng, lat):
        if self.shop and self.role == ROLE_CUSTOMER:
            if name and address and telephone and items:
                order = {
                    'time': self.__CurrentTime(),
                    'name': name,
                    'address': address,
                    'telephone': telephone,
                    'items': items,
                    'note': note,
                    'stat': 0
                }
                if lng and lat and lng != '0' and lat != '0':
                    order['point'] = f'{lng},{lat}'
                mc.hmset(f'{self.shop}-{self.__NewId()}', order)
                LOG_INFO(f'new order in shop {self.shop}')
                return True
        LOG_WARN(f'new order in shop {self.shop} failed')
        return False

    def GetOrders(self):
        orders = []
        if self.shop and self.role in ROLES:
            shopOrderCount = self.GetShopOrderCount(self.shop)
            for i in range(1, shopOrderCount + 1):
                entry = f'{self.shop}-{i}'
                order = mc.hgetall(entry)
                if order:
                    order = self.__FillOrder(order, self.role, i)
                    if order:
                        orders.append(order)
                else:
                    LOG_WARN(f'get order {entry} failed')
        else:
            LOG_WARN('get order failed, no shop or invalid role')
        return orders

    def UpdateOrder(self, id, stat):
        if self.shop and self.role == ROLE_SALER and stat in (-1, 0, 1, 2, 3):
            if mc.hexists(f'{self.shop}-{id}', 'stat'):
                mc.hset(f'{self.shop}-{id}', 'stat', stat)
                return True
            else:
                LOG_WARN('update order failed, no key')
        else:
            LOG_WARN('update order failed, no shop or invalid role or invalid stat')
        return False

    def CountOrder(self):
        if self.shop and self.role == ROLE_SALER:
            return self.GetShopOrderCount(self.shop)
        else:
            return 0

# define http handlers
class ErrorHandler(RequestHandler):
    def get(self):
        self.write('散了散了，别瞅了')

    def write_error(self, status_code, **kwargs):
        LOG_ERROR('%d - %s' % (status_code, self.request))

class HandlerBase(RequestHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.json_args = None

    def prepare(self):
        if self.request.headers.get('Content-Type', '').startswith('application/json'):
            self.json_args = json.loads(self.request.body)

    def GetFromRequest(self, param, default):
        if self.json_args is not None:
            if param in self.json_args:
                return self.json_args[param]
            else:
                return default
        else:
            return self.get_argument(param, default)

    def Response(self, result):
        template_path = None
        if isinstance(result, dict):
            template_path = result.get(TEMPLATE_MARK)
        if template_path:
            self.render(template_path, **result)
        else:
            self.write(json.dumps(result))

class LoadHandler(HandlerBase):
    def get(self):
        shop = self.GetFromRequest("shop", "")
        role = self.GetFromRequest("role", "")
        if Shop.Valid(shop, role):
            result = {
                TEMPLATE_MARK: 'index.html',
                'shop': shop,
                'role': role
            }
            self.Response(result)
        else:
            self.redirect("/")

class ListHandler(HandlerBase):
    def get(self):
        shop = Shop(self.GetFromRequest("shop", ""), self.GetFromRequest("role", ""))
        if shop.IsValid():
            self.Response(shop.GetOrders())
        else:
            self.redirect("/")

class NewHanlder(HandlerBase):
    def get(self):
        shop = Shop(self.GetFromRequest("shop", ""), self.GetFromRequest("role", ""))
        if shop.IsValid():
            if shop.NewOrder(
                    self.GetFromRequest("name", None),
                    self.GetFromRequest("address", None),
                    self.GetFromRequest("telephone", None),
                    self.GetFromRequest("items", None),
                    self.GetFromRequest("note", ''),
                    self.GetFromRequest("lng", '0'),
                    self.GetFromRequest("lat", '0')):
                result = {'state': 'ok'}
            else:
                result = {'state': 'error', 'msg': '下单失败'}
            self.Response(result)
        else:
            self.redirect("/")

class UpdateHandler(HandlerBase):
    def get(self):
        shop = Shop(self.GetFromRequest("shop", ""), self.GetFromRequest("role", ""))
        if shop.IsValid():
            if shop.UpdateOrder(
                    self.GetFromRequest("id", None),
                    int(self.GetFromRequest("stat", 999))):
                result = {'state': 'ok'}
            else:
                result = {'state': 'error', 'msg': '更新失败'}
            self.Response(result)
        else:
            self.redirect('/')

class CountHandler(HandlerBase):
    def get(self):
        shop = Shop(self.GetFromRequest("shop", ""), self.GetFromRequest("role", ""))
        if shop.IsValid():
            result = {'state': 'ok', 'msg': shop.CountOrder()}
            self.Response(result)
        else:
            self.redirect('/')

def run():
    # setup tornado web server
    settings = dict(static_path=os.path.join(base_dir, 'vuedist', 'static'),
                    template_path=os.path.join(base_dir, 'vuedist'),
                    default_handler_class=LoadHandler)
    webapp = tornado.web.Application(handlers=[
                                                ('/load', LoadHandler),
                                                ('/list', ListHandler),
                                                ('/new', NewHanlder),
                                                ('/update', UpdateHandler),
                                                ('/count', CountHandler)
                                              ],
                                     **settings)
    server = tornado.httpserver.HTTPServer(webapp)
    server.listen(9000)
    tornado.ioloop.IOLoop.instance().start()

def test():
    Shop.NewShop('lanser')

    shopc = Shop(Shop.GenShopKey('lanser', ROLE_CUSTOMER), ROLE_CUSTOMER)
    shopc.NewOrder('张三', '张王里村', '13812345678', '达尔x1 发动机x2', '三点后送货', 0, 0)
    orders = shopc.GetOrders()

    shops = Shop(Shop.GenShopKey('lanser', ROLE_SALER), ROLE_SALER)
    orders = shops.GetOrders()
    shops.UpdateOrder(orders[0]['id'], 1)
    orders = shopc.GetOrders()

    orders = shops.GetOrders()
    shops.UpdateOrder(orders[0]['id'], 2)
    orders = shopc.GetOrders()

    Shop.DelShop('lanser')

if __name__ == '__main__':
    #test()
    run()