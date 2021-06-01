# import pymongo
#
# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# mydb = myclient["mytest"]
# mycol = mydb["site2"]
#
# mylist = [
#     {"_id": 1, "name": "RUNOOB", "cn_name": "菜鸟教程"}
# ]
#
# x = mycol.insert_many(mylist)
#
# print(x.inserted_ids)