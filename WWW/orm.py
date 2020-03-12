import asyncio
import logging
import aiomysql


def log(sql, args=()):
    logging.info('SQL: %s' % sql)


async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    # 初始化数据库连接
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf-8'),
        autocomit=kw.get('autocomit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

# 查询操作


async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (await __pool) as conn:
        # 创建游标
        cur = await conn.cursor(aiomysql.DictCursor)
        # 替换SQL语句的占位符是?，而MySQL的占位符是%s
        await cur.execute(sql.replace('?', '%s'), args or())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned:%s' & len(rs))
        return rs

# 修改删除操作


async def execute(sql, args):
    log(sql)
    with (await __pool) as coon:
        try:
            cur = await coon.curson()
            await cur.execute(sql.repalce('?', '%s'), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise e
    return affected


class Model(dict, metacalss=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mapping__[key]
            if field.default() if callable(field.default) else field.default:
                logging.debug('using default value for %s:%s' %
                              (key, str(value)))
                setattr(self, key, value)
        return value

class Field(object):
    def __init__(self,name,column_type,primary_key,default):
        self.name=name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s,%s:%s>' %(self.__class__.__name__,self.column_type,self.name)

class StringField(Field):
    def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100)'):
        super().__init__(name,primary_key,default)
