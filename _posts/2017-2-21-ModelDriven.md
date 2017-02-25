---
layout: post
title:  Struts2中的ModelDriven机制及其运用
date:   2017-02-21 19:25:00 +0800
categories: 技术博客
tag: 轻量级JavaEE框架技术
---

* content
{:toc}

一、为什么需要ModelDriven
============================
所谓`ModelDriven`，意思是直接把实体类当成页面数据的收集对象。比如，有实体类`User`如下：<br>

```java
package cn.com.leadfar.struts2.actions;
 
public class User {
    private int id;
    private String username;
    private String password;
    private int age;
    private String address;
    
    public String getUsername() {
       return username;
    }
    public void setUsername(String username) {
       this.username = username;
    }
    public String getPassword() {
       return password;
    }
    public void setPassword(String password) {
       this.password = password;
    }
    public int getAge() {
       return age;
    }
    public void setAge(int age) {
       this.age = age;
    }
    public String getAddress() {
       return address;
    }
    public void setAddress(String address) {
       this.address = address;
    }
    public int getId() {
       return id;
    }
    public void setId(int id) {
       this.id = id;
    }   
}
```

假如你要写一个`Action`，用来添加`User`。<br>
+ 第一种做法是直接在`Action`中定义所有需要的属性，然后在JSP中直接用属性名称来提交数据：<br>
> UserAction.java
```java
public class UserAction {
    private int id;
    private String username;
    private String password;
    private int age;
    private String address;
 
    public String add(){
      
       User user = new User();
       user.setId(id);
       user.setUsername(username);
       user.setPassword(password);
       user.setAge(age);
       user.setAddress(address);
      
       new UserManager().addUser(user);
      
       return "success";
    }
   
    public int getId() {
       return id;
    }
    public void setId(int id) {
       this.id = id;
    }
    public String getUsername() {
       return username;
    }
    public void setUsername(String username) {
       this.username = username;
    }
    public String getPassword() {
       return password;
    }
    public void setPassword(String password) {
       this.password = password;
    }
    public int getAge() {
       return age;
    }
    public void setAge(int age) {
       this.age = age;
    }
    public String getAddress() {
       return address;
    }
    public void setAddress(String address) {
       this.address = address;
    }  
}
```

> add_input.jsp
```html
<form action="test/user.action" method="post">
	<input type="hidden" name="method:add">username:
	<input type="text" name="username"> <br/>password:
	<input type="text" name="password"> <br/>age:
	<input type="text" name="age"> <br/>address:
	<input type="text" name="address"> <br/>
	<input type="submit" name="submit" value="添加用户">
</form>
```

上述做法不好之处是：如果实体类的属性非常多，那么`Action`中也要定义相同的属性。<br>

+ 第二种做法是将User对象定义到`UserAction`中，然后在JSP中通过`user`属性来给`user`赋值：<br>

> UserAction
```java
public class UserAction {
   
    private User user;
   
    public String add(){
 
       new UserManager().addUser(user);
      
       return "success";
    }
 
    public User getUser() {
       return user;
    }
    public void setUser(User user) {
       this.user = user;
    }  
}
```

> add_input.jsp
```html
<form action="test/user.action" method="post">
	<input type="hidden" name="method:add">username:
	<input type="text" name="user.username"> <br/>password:
	<input type="text" name="user.password"> <br/>age:
	<input type="text" name="user.age"> <br/>address:
	<input type="text" name="user.address"> <br/>
    <input type="submit" name="submit" value="添加用户">
</form>
```

这种做法不好的地方是：JSP页面上表单域中的命名变得太长。<br>

+ 第三种做法是利用`ModelDriven`机制，让`UserAction`实现一个`ModelDriven`接口，同时实现接口中的方法：`getModel()`。如下所示：<br>

> UserAction
```java
public class UserAction implements ModelDriven{
   
    private User user;
   
    @Override
    public Object getModel() {
       if(user == null){
           user = new User();
       }
       return user;
    }
 
    public String add(){
 
       new UserManager().addUser(user);
      
       return "success";
    }
 
    public User getUser() {
       return user;
    } 
    public void setUser(User user) {
       this.user = user;
    }
}
```

> add_input.jsp
```html
<form action="test/user.action" method="post">
    <input type="hidden" name="method:add">username:
    <input type="text" name="user.username"> <br/>password:
    <input type="text" name="user.password"> <br/>age:
    <input type="text" name="user.age"> <br/>address:
    <input type="text" name="user.address"> <br/>
	<input type="submit" name="submit" value="添加用户">
</form>
```

可见，第三种做法是比较好的，Action和JSP写起来都比较简单。<br>

二、ModelDriven的机制
============================
`ModelDriven`背后的机制就是`ValueStack`。界面通过：`username/age/address`这样的名称，就能够被直接赋值给`user`对象，这证明`user`对象正是`ValueStack`中的一个`root`对象。<br>
那么，为什么`user`对象会在`ValueStack`中呢？它是什么时候被压入`ValueStack的`呢？答案是：ModelDrivenInterceptor（关于Interceptor的概念，请参考后续章节的说明）。`ModelDrivenInterceptor`是缺省的拦截器链的一部分，当一个请求经过`ModelDrivenInterceptor`的时候，在这个拦截器中，会判断当前要调用的`Action`对象是否实现了`ModelDriven`接口，如果实现了这个接口，则调用`getModel()`方法，并把返回值（本例是返回`user`对象）压入`ValueStack`。<br>
请看`ModelDrivenInterceptor`的代码：<br>
```java
public class ModelDrivenInterceptor extends AbstractInterceptor {
 
    protected boolean refreshModelBeforeResult = false;
 
    public void setRefreshModelBeforeResult(boolean val) {
        this.refreshModelBeforeResult = val;
    }
 
    @Override
    public String intercept(ActionInvocation invocation) throws Exception {
        Object action = invocation.getAction();
 
        if (action instanceof ModelDriven) {
            ModelDriven modelDriven = (ModelDriven) action;
            ValueStack stack = invocation.getStack();
            Object model = modelDriven.getModel();
            if (model !=  null) {
              stack.push(model);
            }
            if (refreshModelBeforeResult) {
                invocation.addPreResultListener(new RefreshModelBeforeResult(modelDriven, model));
            }
        }
        return invocation.invoke();
    }
}
```

从`ModelDrivenInterceptor`中，即可以看到model对象被压入`ValueStack`中。其中的`refreshModelBeforeResult`是为了接下来描述的一个问题而提供的解决方法。

三、理解常见的陷阱及其解决方法
============================
假设我们要更新一个实体对象，那么第一步首先是打开更新界面，请看下述模拟打开更新界面的代码：
```java
public class UserAction implements ModelDriven{
   
    private User user;
   
    @Override
    public Object getModel() {
       if(user == null){
           user = new User();
           //user.setUsername("这是原来的User对象");
       }
       return user;
    }
   
    public String updateInput(){
      
       //根据ID，查询数据库，得到User对象
       user = new UserManager().findUserById(user.getId());
      
      
       return "update_input";
    }
}
```

上述代码中，`new UserManager().findUserById(user.getId());`这一行，将从数据库中查询相应的记录，同时转换为User对象返回。而`return “update_input”`将转向更新显示页面。
更新页面如下：
```html
<form action="test/user.action" method="post">
    <input type="hidden" name="method:update">id:
    <input type="text" name="id" value="<s:property value="id"/>"> <br/>username:
    <input type="text" name="username" value="<s:property value="username"/>"> <br/>password:
    <input type="text" name="password" value="<s:property value="password"/>"> <br/>age:
    <input type="text" name="age" value="<s:property value="age"/>"> <br/>address:
    <input type="text" name="address" value="<s:property value="address"/>"> <br/>
    <input type="submit" name="submit" value="更新用户">
</form>
```

上述代码运行起来之后，你在更新界面上将看不到数据（id属性有值，其它属性无显示）。关键的原因是在执行到`updateInput`之前，`user`对象（在`getMode()`方法中创建的对象）被压到`ValueStack`中，这时候，`UserAction`和`ValueStack`都指向同一个`user`对象；但紧接着，UserAction中的user被一个新的user对象覆盖，这时候，`UserAction`和`ValueStack`不再指向同一个`user`对象！`ValueStack`中是旧的`user`对象，而`UserAction`中是新的`user`对象！我们在JSP中，直接通过`username/address`等直接访问，当然是要访问`ValueStack`中的旧`user`对象，所以它们的属性都是空的(id属性除外)。<br>
 
理解上述问题很重要，当你理解了问题，那么问题的解决方法就可以有很多了：
比如，你可以把新对象的属性拷贝到旧对象上；比如，你可以先把旧对象从`ValueStack`中移除，然后再把新对象压入`ValueStack`等。<br>
在最新的struts2版本中，`ModelDrivenInterceptor`提供了一个配置参数：`refreshModelBeforeResult`，只要将它定义为true，上述问题就被解决了！`Struts2`的解决方案就是：先把旧的model对象从ValueStack中移除，然后再把新的model对象压入`ValueStack`。<br>