from . import mongo, bcrypt
from bson import ObjectId

def create_user(username, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = {
        "username": username,
        "password": hashed_password
    }
    result = mongo.db.users.insert_one(user)
    return result

def find_user_by_username(username):
    return mongo.db.users.find_one({"username": username})



def update_user_images(username, image_type, file):
    image_collection = mongo.db.images
    image_data = {
        "filename": f"{image_type}.jpg",  # Change to specific type
        "content_type": file.content_type,
        "data": file.read(),
        "type": image_type  # Add a type field for differentiation
    }
    
    user_images = image_collection.find_one({"username": username})
    
    if user_images and "images" in user_images:
        images = user_images["images"]
        
        # Check if there's already an image of this type and replace it
        image_found = False
        for img in images:
            if img["type"] == image_type:
                # Replace existing image of this type
                image_data["_id"] = img["_id"]
                image_collection.update_one(
                    {"username": username, "images._id": img["_id"]},
                    {"$set": {"images.$": image_data}}
                )
                image_found = True
                break
        
        if not image_found:
            # Add new image if not found
            image_data["_id"] = str(ObjectId())
            images.append(image_data)
            result = image_collection.update_one(
                {"username": username},
                {"$set": {"images": images}}
            )
            
            if result.modified_count > 0:
                return {"success": "Image collection updated successfully"}
            else:
                return {"error": "Failed to update image collection"}
        else:
            return {"success": "Image updated successfully"}
    else:
        # Create a new image list for the user
        new_user_images = {
            "username": username,
            "images": [image_data]
        }
        result = image_collection.insert_one(new_user_images)
        
        if result.inserted_id:
            return {"success": "Image collection updated successfully"}
        else:
            return {"error": "Failed to insert new image collection"}
def get_user_image_collection(username):
    return mongo.db.images.find_one({"username": username})

def delete_user_images(username):
    result = mongo.db.images.delete_many({"username": username})
    return result.deleted_count