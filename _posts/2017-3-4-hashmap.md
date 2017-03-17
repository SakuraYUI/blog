---
layout: post
title:  HashMap的学习与研究
date:   2017-03-04 15:00:00 +0800
categories: 技术博客
tag: 数据结构与算法
---

* content
{:toc}



一、HashMap工作原理
========================

1.两个方法
------------------------

> hashCode方法

```java
/** JNI，调用底层其它语言实现 */  
public native int hashCode();  
  
/** 默认同==，直接比较对象 */  
public boolean equals(Object obj) {  
    return (this == obj);  
}  
```

> equals方法
```java
public boolean equals(Object anObject) {  
    if (this == anObject) {  
        return true;  
    }  
    if (anObject instanceof String) {  
        String anotherString = (String) anObject;  
        int n = value.length;  
        if (n == anotherString.value.length) {  
            char v1[] = value;  
            char v2[] = anotherString.value;  
            int i = 0;  
            // 逐个判断字符是否相等  
            while (n-- != 0) {  
                if (v1[i] != v2[i])  
                        return false;  
                i++;  
            }  
            return true;  
        }  
    }  
    return false;  
}  
```

重写equals要满足几个条件：

+ 自反性：对于任何非空引用值 x，x.equals(x) 都应返回 true。 

+ 对称性：对于任何非空引用值 x 和 y，当且仅当 y.equals(x) 返回 true 时，x.equals(y) 才应返回 true。

+ 传递性：对于任何非空引用值 x、y 和 z，如果 x.equals(y) 返回 true，并且 y.equals(z) 返回 true，那么 x.equals(z) 应返回 true。 

+ 一致性：对于任何非空引用值 x 和 y，多次调用 x.equals(y) 始终返回 true 或始终返回 false，前提是对象上 equals 比较中所用的信息没有被修改。 
对于任何非空引用值 x，x.equals(null) 都应返回 false。

Object 类的 equals 方法实现对象上差别可能性最大的相等关系；即，对于任何非空引用值 x 和 y，当且仅当 x 和 y 引用同一个对象时，此方法才返回 true（x == y 具有值 true）。 当此方法被重写时，通常有必要重写 hashCode 方法，以维护 hashCode 方法的常规协定，该协定声明相等对象必须具有相等的哈希码。

下面来说说hashCode方法，这个方法我们平时通常是用不到的，它是为哈希家族的集合类框架(HashMap、HashSet、HashTable)提供服务，hashCode 的常规协定是：

+ 在 Java 应用程序执行期间，在同一对象上多次调用 hashCode 方法时，必须一致地返回相同的整数，前提是对象上 equals 比较中所用的信息没有被修改。从某一应用程序的一次执行到同一应用程序的另一次执行，该整数无需保持一致。 

+ 如果根据 equals(Object) 方法，两个对象是相等的，那么在两个对象中的每个对象上调用 hashCode 方法都必须生成相同的整数结果。 

+ 以下情况不是必需的：如果根据 equals(java.lang.Object) 方法，两个对象不相等，那么在两个对象中的任一对象上调用 hashCode 方法必定会生成不同的整数结果。但是，程序员应该知道，为不相等的对象生成不同整数结果可以提高哈希表的性能。

当我们看到实现这两个方法有这么多要求时，立刻凌乱了，幸好有IDE来帮助我们，Eclipse中可以通过快捷键alt+shift+s调出快捷菜单，选择Generate hashCode() and equals()，根据业务需求，勾选需要生成的属性，确定之后，这两个方法就生成好了，我们通常需要在JavaBean对象中重写这两个方法。

2.HashMap类结构
-----------------------

HashMap是最常用的集合类框架之一，它实现了Map接口，所以存储的元素也是键值对映射的结构，并允许使用null值和null键，其内元素是无序的，如果要保证有序，可以使用LinkedHashMap。HashMap是线程不安全的。HashMap的类结构如下：

```
java.lang.Object
  java.util.AbstractMap<K,V>
    java.util.HashMap<K,V>
```

所有已实现的接口：
```
Serializable,Cloneable,Map<K,V>
```
直接已知子类：
```
LinkedHashMap,PrinterStateReasons
```

HashMap中我们最长用的就是put(K, V)和get(K)。我们都知道，HashMap的K值是唯一的，那如何保证唯一性呢？

我们首先想到的是用equals比较，没错，这样可以实现，但随着内部元素的增多，put和get的效率将越来越低，这里的时间复杂度是O(n)，假如有1000个元素，put时需要比较1000次。实际上，HashMap很少会用到equals方法，因为其内通过一个哈希表管理所有元素，哈希是通过hash单词音译过来的，也可以称为散列表，哈希算法可以快速的存取元素，当我们调用put存值时，HashMap首先会调用K的hashCode方法，获取哈希码，通过哈希码快速找到某个存放位置，这个位置可以被称之为bucketIndex，通过上面所述hashCode的协定可以知道，如果hashCode不同，equals一定为false，如果hashCode相同，equals不一定为true。所以理论上，hashCode可能存在冲突的情况，有个专业名词叫碰撞，当碰撞发生时，计算出的bucketIndex也是相同的，这时会取到bucketIndex位置已存储的元素，最终通过equals来比较，equals方法就是哈希码碰撞时才会执行的方法，所以前面说HashMap很少会用到equals。HashMap通过hashCode和equals最终判断出K是否已存在，如果已存在，则使用新V值替换旧V值，并返回旧V值，如果不存在 ，则存放新的键值对<K, V>到bucketIndex位置。

