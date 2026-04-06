# 🚀 VPVS Backend Postman Collection

## 🌐 **BASE URL**
```
https://vpvs-backend.onrender.com
```

---

## 🔐 **AUTHENTICATION ENDPOINTS**

### **1. User Signup**
```http
POST {{base_url}}/api/profiles/signup
Content-Type: application/json

{
  "username": "testuser123",
  "email": "testuser123@example.com",
  "password": "password123",
  "phone": "9876543210",
  "dob": "2000-01-01",
  "is_admin": false
}
```

### **2. User Login**
```http
POST {{base_url}}/api/auth/login
Content-Type: application/json

{
  "username": "testuser123",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_id",
    "username": "testuser123",
    "email": "testuser123@example.com",
    "is_admin": false
  },
  "token": "jwt_token_here"
}
```

---

## 📝 **POSTS ENDPOINTS**

### **3. Get All Posts**
```http
GET {{base_url}}/api/posts
```

### **4. Get Single Post**
```http
GET {{base_url}}/api/posts/{{post_id}}
```

### **5. Create Post (Admin Only)**
```http
POST {{base_url}}/api/posts
Authorization: Bearer {{admin_token}}
Content-Type: multipart/form-data

title: "Test Post Title"
description: "This is a test post description"
image: [file_upload]
```

### **6. Delete Post (Admin Only)**
```http
DELETE {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{admin_token}}
```

### **7. Get Post with Stats**
```http
GET {{base_url}}/api/posts/{{post_id}}/with-stats
```

---

## 💬 **COMMENTS ENDPOINTS**

### **8. Get Post Comments**
```http
GET {{base_url}}/api/posts/{{post_id}}/comments
```

### **9. Add Comment to Post**
```http
POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{user_token}}
Content-Type: application/json

{
  "comment": "This is a test comment",
  "username": "testuser123"
}
```

### **10. Get Comments (Legacy)**
```http
GET {{base_url}}/api/comments?postId={{post_id}}
```

### **11. Add Comment (Legacy)**
```http
POST {{base_url}}/api/comments
Content-Type: application/json

{
  "postId": "post_id_here",
  "username": "testuser123",
  "comment": "This is a test comment"
}
```

---

## ❤️ **LIKES ENDPOINTS**

### **12. Get Post Likes**
```http
GET {{base_url}}/api/posts/{{post_id}}/likes
```

### **13. Like Post**
```http
POST {{base_url}}/api/posts/{{post_id}}/like
Authorization: Bearer {{user_token}}
Content-Type: application/json

{
  "username": "testuser123"
}
```

### **14. Unlike Post**
```http
POST {{base_url}}/api/posts/{{post_id}}/unlike
Authorization: Bearer {{user_token}}
Content-Type: application/json

{
  "username": "testuser123"
}
```

### **15. Get Likes (Legacy)**
```http
GET {{base_url}}/api/likes?postId={{post_id}}
```

### **16. Add Like (Legacy)**
```http
POST {{base_url}}/api/likes
Content-Type: application/json

{
  "postId": "post_id_here",
  "username": "testuser123"
}
```

### **17. Remove Like (Legacy)**
```http
DELETE {{base_url}}/api/likes
Content-Type: application/json

{
  "postId": "post_id_here",
  "username": "testuser123"
}
```

---

## 💰 **EXPENSES ENDPOINTS**

### **18. Get Expenses**
```http
GET {{base_url}}/api/expenses?view=day
Authorization: Bearer {{user_token}}
```

### **19. Create Expense**
```http
POST {{base_url}}/api/expenses
Authorization: Bearer {{user_token}}
Content-Type: application/json

{
  "description": "Test Expense",
  "amount": 100.50,
  "type": "debit",
  "date": "2024-01-01",
  "group_id": null
}
```

### **20. Update Expense**
```http
PUT {{base_url}}/api/expenses/{{expense_id}}
Authorization: Bearer {{user_token}}
Content-Type: application/json

{
  "description": "Updated Expense",
  "amount": 150.75,
  "type": "credit",
  "date": "2024-01-02",
  "group_id": null
}
```

### **21. Delete Expense**
```http
DELETE {{base_url}}/api/expenses/{{expense_id}}
Authorization: Bearer {{user_token}}
```

---

## 👥 **EXPENSE GROUPS ENDPOINTS**

### **22. Get Expense Groups**
```http
GET {{base_url}}/api/expense-groups
Authorization: Bearer {{user_token}}
```

### **23. Create Expense Group (Admin Only)**
```http
POST {{base_url}}/api/expense-groups
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "name": "Test Group",
  "description": "This is a test expense group"
}
```

---

## 👤 **PROFILE ENDPOINTS**

### **24. Get Profile**
```http
GET {{base_url}}/api/profiles/{{username}}
```

---

## 🔍 **HEALTH AND SYSTEM ENDPOINTS**

### **25. Health Check**
```http
GET {{base_url}}/api/health
```

---

## 📋 **POSTMAN VARIABLES**

### **Environment Variables:**
```json
{
  "base_url": "https://vpvs-backend.onrender.com",
  "user_token": "your_jwt_token_here",
  "admin_token": "your_admin_jwt_token_here",
  "post_id": "your_post_id_here",
  "expense_id": "your_expense_id_here",
  "username": "testuser123"
}
```

---

## 🧪 **TESTING SEQUENCE**

### **1. Authentication Flow:**
1. **Signup User**: Use endpoint #1
2. **Login User**: Use endpoint #2
3. **Save Token**: Copy response token to environment variables

### **2. Admin Setup:**
1. **Create Admin User**: Use endpoint #1 with `"is_admin": true`
2. **Login Admin**: Use endpoint #2
3. **Save Admin Token**: Copy to environment variables

### **3. Posts Testing:**
1. **Get Posts**: Use endpoint #3
2. **Create Post**: Use endpoint #5 (admin only)
3. **Get Single Post**: Use endpoint #4
4. **Delete Post**: Use endpoint #6 (admin only)

### **4. Comments Testing:**
1. **Get Comments**: Use endpoint #8
2. **Add Comment**: Use endpoint #9
3. **Verify Comment**: Use endpoint #8 again

### **5. Likes Testing:**
1. **Get Likes**: Use endpoint #12
2. **Like Post**: Use endpoint #13
3. **Unlike Post**: Use endpoint #14
4. **Verify Like Count**: Use endpoint #12 again

### **6. Expenses Testing:**
1. **Get Expenses**: Use endpoint #18
2. **Create Expense**: Use endpoint #19
3. **Update Expense**: Use endpoint #20
4. **Delete Expense**: Use endpoint #21

### **7. Expense Groups Testing:**
1. **Get Groups**: Use endpoint #22
2. **Create Group**: Use endpoint #23 (admin only)

---

## 📊 **EXPECTED RESPONSES**

### **Success Responses:**
- **200 OK**: Successful GET/PUT/DELETE
- **201 Created**: Successful POST
- **401 Unauthorized**: Missing/invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **400 Bad Request**: Invalid input data

### **Error Response Format:**
```json
{
  "error": "Error message here"
}
```

---

## 🔧 **POSTMAN IMPORT**

### **Collection JSON:**
```json
{
  "info": {
    "name": "VPVS Backend API",
    "description": "Complete API testing collection for VPVS backend",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://vpvs-backend.onrender.com",
      "type": "string"
    },
    {
      "key": "user_token",
      "value": "",
      "type": "string"
    },
    {
      "key": "admin_token",
      "value": "",
      "type": "string"
    },
    {
      "key": "post_id",
      "value": "",
      "type": "string"
    },
    {
      "key": "expense_id",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "User Signup",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"testuser123\",\n  \"email\": \"testuser123@example.com\",\n  \"password\": \"password123\",\n  \"phone\": \"9876543210\",\n  \"dob\": \"2000-01-01\",\n  \"is_admin\": false\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/profiles/signup",
              "host": ["{{base_url}}"],
              "path": ["api","profiles","signup"]
            }
          }
        },
        {
          "name": "User Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"testuser123\",\n  \"password\": \"password123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/auth/login",
              "host": ["{{base_url}}"],
              "path": ["api","auth","login"]
            }
          }
        }
      ]
    }
  ]
}
```

---

## 🎯 **QUICK TEST URLS**

### **Copy-Paste URLs:**

1. **Health Check**: `https://vpvs-backend.onrender.com/api/health`
2. **Get Posts**: `https://vpvs-backend.onrender.com/api/posts`
3. **User Signup**: `https://vpvs-backend.onrender.com/api/profiles/signup`
4. **User Login**: `https://vpvs-backend.onrender.com/api/auth/login`
5. **Get Expenses**: `https://vpvs-backend.onrender.com/api/expenses`
6. **Get Expense Groups**: `https://vpvs-backend.onrender.com/api/expense-groups`

---

## 🚀 **READY FOR TESTING**

All endpoints are live and ready for testing with Postman. Use the provided collection to test all functionality of the VPVS backend on production.

**🌟 Backend URL**: https://vpvs-backend.onrender.com
