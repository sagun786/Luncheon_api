#TODO: configure mongoclient as decorator

import datetime
import pprint
from bson.objectid import ObjectId

def prepare(object):
    """Converts _id from ObjectId to string."""
    object['_id'] = str(object['_id'])
    
    return object

def get_user(nickname, email, mongo):

    query = {'$or': [{'nickname': nickname}, {'email': email}]}

    with mongo:

        user = mongo.db.users.find_one(query)

        return user

def check_if_today_is_registered(user, mongo):

    timestamp = user["registered"]["timestamp"]

    result = {"error": None, "data": None}

    pipeline = [
        {"$match": {"_id": user["_id"]}},
        {"$unwind": {"path": "$registered"}},
        {"$project": { "_id": 0, "today": {"$cond": [{"$eq": ["$registered.timestamp", timestamp]}, "True", "False"]}}}
    ]

    with mongo:
        try:
            for data in mongo.db.users.aggregate(pipeline):

                if data["today"] == "True":
                    result["data"] = True
                    result["error"] = {"message": "lunch already registered"}

            
            result["data"] = False

            return result

        except Exception as e:
            print(e)
            result["error"] = {"message": "could not check if date matched"}
            return result

def register_lunch(user, mongo, user_exists=False):

    filter_by = {"_id": user["_id"]}

    update_to_apply = {"$set": 
        {
            "_id": user["_id"],
            "nickname": user["nickname"], 
            "email": user["email"]
        },
        "$push": {"registered": user["registered"]}
    }

    if user_exists is True:

        today_is_registered = check_if_today_is_registered(user, mongo)

        if today_is_registered["error"] is not None:
            payload = {"status": False, "error": today_is_registered["error"]}
            return payload

    with mongo:
        try:     
            mongo.db.users.update_one(filter_by, update_to_apply, upsert=True)

            payload = {"status": True, "error": None}
            
            return payload  

        except Exception as e:
            print(e)
            payload = {"status": False, "error": {"message": "Error when registering lunch for today"}}

        return payload   

def delete_user(_id, mongo):
    
    status = False
    with mongo:
        try:
            result = mongo.db.users.delete_one({"_id": ObjectId(_id)})
            print(result)
            status = True
            return {"status": status} 
        except Exception as e:
            return {"status": status, "error": {"message": e}}

def delete_timestamp(user_id, timestamp_id, mongo):
    
    status = False
    filter_by = {"_id": ObjectId(user_id)}
    delete = {"$pull": {"registered": {"_id": ObjectId(timestamp_id)}}}
    with mongo:
        try:
            mongo.db.users.update_one(filter_by, delete)
            status = True
            return {"status": status}

        except Exception as e:

            return {"status": status, "error": {"message": e}}



    





    
