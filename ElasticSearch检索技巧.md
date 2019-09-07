# ElasticSearch检索技巧

关系数据库 ⇒ 数据库 ⇒ 表 ⇒ 行 ⇒ 列(Columns)

Elasticsearch ⇒ 索引 ⇒ 类型 ⇒ 文档 ⇒ 字段(Fields)

### 数据准备

为了讲解不同类型 ES 检索，我们将要对包含以下类型的文档集合进行检索：

```
title               标题
authors             作者
summary             摘要
publish_date        发布日期
num_reviews         评论数
publisher           出版社
```

首先，我们借助 bulk API 批量创建新的索引并提交数据

```json
# 设置索引 settings
PUT /bookdb_index
{"settings": 
    {"number_of_shards": 2,
    "number_of_replicas": 0},
}

# bulk 提交数据
POST /bookdb_index/book/_bulk
{"index":{"_id":1}}
{"title":"Elasticsearch: The Definitive Guide",
    "authors":["clinton gormley","zachary tong"],
    "summary":"A distibuted real-time search and analytics engine",
    "publish_date":"2015-02-07",
    "num_reviews":20,
    "publisher":"oreilly"}
{"index":{"_id":2}}
{"title":"Taming Text: How to Find, Organize, and Manipulate It",
    "authors":["grant ingersoll","thomas morton","drew farris"],
    "summary":"organize text using approaches such as full-text search, proper name recognition, clustering, tagging, information extraction, and summarization",
    "publish_date":"2013-01-24",
    "num_reviews":12,
    "publisher":"manning"}
{"index":{"_id":3}}
{"title":"Elasticsearch in Action",
    "authors":["radu gheorge","matthew lee hinman","roy russo"],
    "summary":"build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
    "publish_date":"2015-12-03",
    "num_reviews":18,
    "publisher":"manning"}
{"index":{"_id":4}}
{"title":"Solr in Action",
    "authors":["trey grainger","timothy potter"],
    "summary":"Comprehensive guide to implementing a scalable search engine using Apache Solr",
    "publish_date":"2014-04-05",
    "num_reviews":23,
    "publisher":"manning"}
```



### 查看映射

```
GET /bookdb_index/_mapping
```



### 全文检索（查所有字段）

#### 使用URL检索API

```json
GET bookdb_index/book/_search?q=guide

[Results]
  "hits": {
    "total": 2,
    "max_score": 1.3278645,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1.3278645,
        "_source": {
          "title": "Solr in Action",
          "authors": [
            "trey grainger",
            "timothy potter"
          ],
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "publish_date": "2014-04-05",
          "num_reviews": 23,
          "publisher": "manning"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 1.2871116,
        "_source": {
          "title": "Elasticsearch: The Definitive Guide",
          "authors": [
            "clinton gormley",
            "zachary tong"
          ],
          "summary": "A distibuted real-time search and analytics engine",
          "publish_date": "2015-02-07",
          "num_reviews": 20,
          "publisher": "oreilly"
        }
      }
    ]
  }
```



#### 使用完整ES DSL语句，其中Json body作为请求体

执行结果和上面一样

```json
GET bookdb_index/book/_search
{
  "query": {
    "multi_match": {
      "query": "guide",
      "fields" : ["_all"]
    }
  }
}
```



### 指定单个字段检索

#### URL检索方式

```json
GET bookdb_index/book/_search?q=title:in action

[Results]
  "hits": {
    "total": 2,
    "max_score": 1.6323128,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 1.6323128,
        "_source": {
          "title": "Elasticsearch in Action",
          "authors": [
            "radu gheorge",
            "matthew lee hinman",
            "roy russo"
          ],
          "summary": "build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
          "publish_date": "2015-12-03",
          "num_reviews": 18,
          "publisher": "manning"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1.6323128,
        "_source": {
          "title": "Solr in Action",
          "authors": [
            "trey grainger",
            "timothy potter"
          ],
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "publish_date": "2014-04-05",
          "num_reviews": 23,
          "publisher": "manning"
        }
      }
    ]
  }
```





#### ES DSL检索方式

结果数的表示方式：size
偏移值的表示方式：from
指定返回字段 的表示方式 ：_source
高亮显示 的表示方式 ：highliaght

```json
GET bookdb_index/book/_search
{
  "query": {
    "match": {
      "title": "in action"
    }
  },
  "size": 2,
  "from": 0,
  "_source": ["title", "summary", "publish_date"],
  "highlight": {
    "fields": {
      "title": {}
    }
  }
}

[Results]
  "hits": {
    "total": 2,
    "max_score": 1.6323128,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 1.6323128,
        "_source": {
          "summary": "build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        },
        "highlight": {
          "title": [
            "Elasticsearch <em>in</em> <em>Action</em>"
          ]
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1.6323128,
        "_source": {
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        },
        "highlight": {
          "title": [
            "Solr <em>in</em> <em>Action</em>"
          ]
        }
      }
    ]
  }
```



还可以用后面的Term/Terms检索（指定字段检索）





### 指定多个字段检测

```json
GET bookdb_index/book/_search
{
  "query": {
    "multi_match": {
      "query": "guide", 
      "fields": ["title", "summary"]
    }
  }
}

[Results]
  "hits": {
    "total": 3,
    "max_score": 2.0281231,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 2.0281231,
        "_source": {
          "title": "Elasticsearch: The Definitive Guide",
          "authors": [
            "clinton gormley",
            "zachary tong"
          ],
          "summary": "A distibuted real-time search and analytics engine",
          "publish_date": "2015-02-07",
          "num_reviews": 20,
          "publisher": "oreilly"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1.3278645,
        "_source": {
          "title": "Solr in Action",
          "authors": [
            "trey grainger",
            "timothy potter"
          ],
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "publish_date": "2014-04-05",
          "num_reviews": 23,
          "publisher": "manning"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 1.0333893,
        "_source": {
          "title": "Elasticsearch in Action",
          "authors": [
            "radu gheorge",
            "matthew lee hinman",
            "roy russo"
          ],
          "summary": "build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
          "publish_date": "2015-12-03",
          "num_reviews": 18,
          "publisher": "manning"
        }
      }
    ]
  }
```





### Boosting提升某字段得分的检索( Boosting)

由于我们正在多个字段进行搜索，我们可能希望提高某一字段的得分。 在下面的例子中，我们将“摘要”字段的得分提高了3倍，以增加“摘要”字段的重要性，从而提高文档 4 的相关性。

```json
GET bookdb_index/book/_search    # 重要点summary^3
{
  "query": {
    "multi_match": {
      "query": "elasticsearch guide", 
      "fields": ["title", "summary^3"]
    }
  },
  "_source": ["title", "summary", "publish_date"]
}

[Results]
  "hits": {
    "total": 3,
    "max_score": 3.9835935,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 3.9835935,
        "_source": {
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 3.1001682,
        "_source": {
          "summary": "build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 2.0281231,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      }
    ]
  }
```





### Bool检索( Bool Query)

可以使用 AND / OR / NOT 运算符来微调我们的搜索查询，以提供更相关或指定的搜索结果。

在搜索API中是通过bool查询来实现的。 bool查询接受 must 参数（等效于AND），一个 must_not 参数（相当于NOT）或者一个 should 参数（等同于OR）。

例如，如果我想在标题中搜索一本名为 "Elasticsearch" 或 "Solr" 的书，AND由 "clinton gormley" 创作，但NOT由 "radu gheorge" 创作

```json
GET bookdb_index/book/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "bool": {
            "should": [
              {"match": {"title": "Elasticsearch"}},
              {"match": {"title": "Solr"}}
            ]
          }
        },
        {
          "match": {"authors": "clinton gormely"}
        }
      ],
      "must_not": [
        {
          "match": {"authors": "radu gheorge"}
        }
      ]
    }
  }
}

[Results]
  "hits": {
    "total": 1,
    "max_score": 2.0749094,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 2.0749094,
        "_source": {
          "title": "Elasticsearch: The Definitive Guide",
          "authors": [
            "clinton gormley",
            "zachary tong"
          ],
          "summary": "A distibuted real-time search and analytics engine",
          "publish_date": "2015-02-07",
          "num_reviews": 20,
          "publisher": "oreilly"
        }
      }
    ]
  }
```

**关于bool查询中的should**， 有两种情况：

- 当should的同级存在must的时候，should中的条件可以满足也可以不满足，满足的越多得分越高
- 当没有must的时候，默认should中的条件至少要满足一个





### Fuzzy 模糊检索( Fuzzy Queries)

在 Match检索 和多匹配检索中可以**启用模糊匹配来捕捉拼写错误**。 基于与原始词的 [Levenshtein](https://link.juejin.im/?target=https%3A%2F%2Fzh.wikipedia.org%2Fwiki%2F%E8%90%8A%E6%96%87%E6%96%AF%E5%9D%A6%E8%B7%9D%E9%9B%A2)距离来指定模糊度

```json
GET bookdb_index/book/_search
{
  "query": {
    "multi_match": {
      "query": "comprihensiv guide",
      "fields": ["title","summary"],
      "fuzziness": "AUTO"
    }
  },
  "_source": ["title","summary","publish_date"],
  "size": 2
}

[Results]
  "hits": {
    "total": 2,
    "max_score": 2.4344182,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 2.4344182,
        "_source": {
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 1.2871116,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      }
    ]
  }
```

"AUTO" 的模糊值相当于当字段长度大于5时指定值2。但是，设置80％的拼写错误的编辑距离为1，将模糊度设置为1可能会提高整体搜索性能。 有关更多信息， [Typos and Misspellingsch](https://link.juejin.im/?target=https%3A%2F%2Fwww.elastic.co%2Fguide%2Fen%2Felasticsearch%2Fguide%2Fcurrent%2Ffuzzy-matching.html)





### Wildcard Query 通配符检索

通配符查询允许您指定匹配的模式，而不是整个词组（term）检索

- ？ 匹配任何字符
- - 匹配零个或多个字符

举例，要查找具有以 "t" 字母开头的作者的所有记录，如下所示

```json
GET bookdb_index/book/_search
{
  "query": {
    "wildcard": {
      "authors": {
        "value": "t*"
      }
    }
  },
  "_source": ["title", "authors"],
  "highlight": {
    "fields": {
      "authors": {}
    }
  }
}

[Results]
  "hits": {
    "total": 3,
    "max_score": 1,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 1,
        "_source": {
          "title": "Elasticsearch: The Definitive Guide",
          "authors": [
            "clinton gormley",
            "zachary tong"
          ]
        },
        "highlight": {
          "authors": [
            "zachary <em>tong</em>"
          ]
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "2",
        "_score": 1,
        "_source": {
          "title": "Taming Text: How to Find, Organize, and Manipulate It",
          "authors": [
            "grant ingersoll",
            "thomas morton",
            "drew farris"
          ]
        },
        "highlight": {
          "authors": [
            "<em>thomas</em> morton"
          ]
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1,
        "_source": {
          "title": "Solr in Action",
          "authors": [
            "trey grainger",
            "timothy potter"
          ]
        },
        "highlight": {
          "authors": [
            "<em>trey</em> grainger",
            "<em>timothy</em> potter"
          ]
        }
      }
    ]
  }

```



### 正则表达式检索

```json
POST bookdb_index/book/_search
{
  "query": {
    "regexp": {
      "authors": "t[a-z]*y"
    }
  },
  "_source": ["title", "authors"],
  "highlight": {
    "fields": {
      "authors": {}
    }
  }
}

[Results]
  "hits": {
    "total": 1,
    "max_score": 1,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1,
        "_source": {
          "title": "Solr in Action",
          "authors": [
            "trey grainger",
            "timothy potter"
          ]
        },
        "highlight": {
          "authors": [
            "<em>trey</em> grainger",
            "<em>timothy</em> potter"
          ]
        }
      }
    ]
  }

```





### 匹配短语检索( Match Phrase Query)

匹配短语查询要求查询字符串中的所有词都存在于文档中，按照查询字符串中**指定的顺序**并且**彼此靠近**。

默认情况下，这些词必须完全相邻，但您可以指定偏离值（slop value)，该值指示在仍然考虑文档匹配的情况下词与词之间的偏离值。

```json
GET bookdb_index/book/_search
{
  "query": {
    "multi_match": {
      "query": "search engine",
      "fields": ["title", "summary"],
      "type": "phrase",
      "slop": 3
    }
  },
  "_source": [ "title", "summary", "publish_date" ]
}

[Results]
  "hits": {
    "total": 2,
    "max_score": 0.88067603,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 0.88067603,
        "_source": {
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 0.51429313,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      }
    ]
  }
```

> 注意：在上面的示例中，对于非短语类型查询，文档_id 1通常具有较高的分数，并且显示在文档_id 4之前，因为其字段长度较短。

然而，作为一个短语查询，词与词之间的接近度被考虑在内，所以文档_id 4分数更好





### 匹配词组前缀检索

```json
GET bookdb_index/book/_search
{
  "query": {
    "match_phrase_prefix": {
      "summary": {
        "query": "search en",
        "slop": 3,
        "max_expansions": 10
      }
    }
  },
  "_source": ["title","summary","publish_date"]
}
```





### 字符串检索（ Query String）

query_string查询提供了以简明的简写语法执行多匹配查询 multi_match queries ，布尔查询 bool queries ，提升得分 boosting ，模糊匹配 fuzzy matching ，通配符 wildcards ，正则表达式 regexp 和范围查询 range queries 的方式。

在下面的例子中，我们对 "search algorithm" 一词执行模糊搜索，其中一本作者是 "grant ingersoll" 或 "tom morton"。 我们搜索所有字段，但将提升应用于文档2的摘要字段

```json
GET bookdb_index/book/_search
{
  "query": {
    "query_string": {
      "query": "(saerch~1 algorithm~1) AND (grant ingersoll)  OR (tom morton)",  #~1应该指的是模糊距离
      "fields": ["summary^2","title","authors","publisher"]
    }
  },
  "_source": ["title","summary","authors"],
  "highlight": {
    "fields": {
      "summary": {}
    }
  }
}

[Results]
  "hits": {
    "total": 1,
    "max_score": 3.571021,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "2",
        "_score": 3.571021,
        "_source": {
          "summary": "organize text using approaches such as full-text search, proper name recognition, clustering, tagging, information extraction, and summarization",
          "title": "Taming Text: How to Find, Organize, and Manipulate It",
          "authors": [
            "grant ingersoll",
            "thomas morton",
            "drew farris"
          ]
        },
        "highlight": {
          "summary": [
            "organize text using approaches such as full-text <em>search</em>, proper name recognition, clustering, tagging"
          ]
        }
      }
    ]
  }
```





### 简化的字符串检索 （Simple Query String）

simple_query_string 查询是 query_string 查询的一个版本，更适合用于暴露给用户的单个搜索框， 因为它分别用 `+` / `|` / `-`  替换了 `AND` / `OR` / `NOT` 的使用，并放弃查询的无效部分，而不是在用户出错时抛出异常。

```json
GET bookdb_index/book/_search
{
  "query": {
    "simple_query_string": {
      "query": "(saerch~1 algorithm~1) + (grant ingersoll)  | (tom morton)",
      "fields": ["summary^2","title","authors","publisher"]
    }
  },
  "_source": ["title","summary","authors"],
  "highlight": {
    "fields": {
      "summary": {}
    }
  }
}

[Results]
# 结果同上

```





### Term/Terms检索（指定字段检索）

有时我们对结构化搜索更感兴趣，我们希望在其中找到完全匹配并返回结果

在下面的例子中，我们搜索 Manning Publications 发布的索引中的所有图书（借助 term和terms查询 ）

```json
GET bookdb_index/book/_search
{
  "query": {
    "term": {
      "publisher": {
        "value": "manning"
      }
    }
  },
  "_source" : ["title","publish_date","publisher"]
}

[Results]
  "hits": {
    "total": 3,
    "max_score": 0.35667494,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "2",
        "_score": 0.35667494,
        "_source": {
          "publisher": "manning",
          "title": "Taming Text: How to Find, Organize, and Manipulate It",
          "publish_date": "2013-01-24"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 0.35667494,
        "_source": {
          "publisher": "manning",
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 0.35667494,
        "_source": {
          "publisher": "manning",
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        }
      }
    ]
  }
```



Multiple terms可指定多个关键词进行检索

```json
GET bookdb_index/book/_search
{
  "query": {
    "terms": {
      "publisher": ["oreilly", "manning"]
    }
  }
}
```





### Term排序检索-（Term Query - Sorted）

Term查询和其他查询一样，轻松的实现排序。多级排序也是允许的

```json
GET bookdb_index/book/_search
{
  "query": {
    "term": {
      "publisher": {
        "value": "manning"
      }
    }
  },
  "_source" : ["title","publish_date","publisher"],
  "sort": [{"publisher.keyword": { "order": "desc"}},
    {"title.keyword": {"order": "asc"}}]
}

[Results]
  "hits": {
    "total": 3,
    "max_score": null,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": null,
        "_source": {
          "publisher": "manning",
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        },
        "sort": [
          "manning",
          "Elasticsearch in Action"
        ]
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": null,
        "_source": {
          "publisher": "manning",
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        },
        "sort": [
          "manning",
          "Solr in Action"
        ]
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "2",
        "_score": null,
        "_source": {
          "publisher": "manning",
          "title": "Taming Text: How to Find, Organize, and Manipulate It",
          "publish_date": "2013-01-24"
        },
        "sort": [
          "manning",
          "Taming Text: How to Find, Organize, and Manipulate It"
        ]
      }
    ]
  }
```

> 注意：Elasticsearch 6.x 全文搜索用text类型的字段，排序用不用 text 类型的字段





### 范围检索（Range query）

```json
GET bookdb_index/book/_search
{
  "query": {
    "range": {
      "publish_date": {
        "gte": "2015-01-01",
        "lte": "2015-12-31"
      }
    }
  },
  "_source" : ["title","publish_date","publisher"]
}

[Results]
  "hits": {
    "total": 2,
    "max_score": 1,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 1,
        "_source": {
          "publisher": "oreilly",
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 1,
        "_source": {
          "publisher": "manning",
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        }
      }
    ]
  }
```

> 注意：范围查询适用于日期，数字和字符串类型字段





### 过滤检索（Filtered query）

（5.0版本起已不再存在，不必关注）

过滤的查询允许您过滤查询的结果。 如下的例子，我们在标题或摘要中查询名为“Elasticsearch”的图书，但是我们希望将结果过滤到只有20个或更多评论的结果。

```json
POST /bookdb_index/book/_search
{
    "query": {
        "filtered": {
            "query" : {
                "multi_match": {
                    "query": "elasticsearch",
                    "fields": ["title","summary"]
                }
            },
            "filter": {
                "range" : {
                    "num_reviews": {
                        "gte": 20
                    }
                }
            }
        }
    },
    "_source" : ["title","summary","publisher", "num_reviews"]
}


[Results]
"hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 0.5955761,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "publisher": "oreilly",
          "num_reviews": 20,
          "title": "Elasticsearch: The Definitive Guide"
        }
      }
    ]
```

可以使用bool查询代替上面的

```json
GET bookdb_index/book/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "elasticsearch",
            "fields": ["title","summary"]
          }
        }
      ],
      "filter": {
        "range": {
          "num_reviews": {
            "gte": 20
          }
        }
      }
    }
  },
  "_source" : ["title","summary","publisher", "num_reviews"]
}
```





### 多个过滤器检索（Multiple Filters）

（5.x不再支持，无需关注） 多个过滤器可以通过使用布尔过滤器进行组合。

在下一个示例中，过滤器确定返回的结果必须至少包含20个评论，不得在2015年之前发布，并且应该由oreilly发布

```json
POST /bookdb_index/book/_search
{
    "query": {
        "filtered": {
            "query" : {
                "multi_match": {
                    "query": "elasticsearch",
                    "fields": ["title","summary"]
                }
            },
            "filter": {
                "bool": {
                    "must": {
                        "range" : { "num_reviews": { "gte": 20 } }
                    },
                    "must_not": {
                        "range" : { "publish_date": { "lte": "2014-12-31" } }
                    },
                    "should": {
                        "term": { "publisher": "oreilly" }
                    }
                }
            }
        }
    },
    "_source" : ["title","summary","publisher", "num_reviews", "publish_date"]
}


[Results]
"hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 0.5955761,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "publisher": "oreilly",
          "num_reviews": 20,
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      }
    ]
```





### Function 得分：Field值因子（ Function Score: Field Value Factor）

可能有一种情况，您想要将文档中特定字段的值纳入相关性分数的计算。 这在您希望基于其受欢迎程度提升文档的相关性的情况下是有代表性的场景

在我们的例子中，我们希望增加更受欢迎的书籍（按评论数量判断）。 这可以使用field_value_factor函数得分

```json
GET bookdb_index/book/_search
{
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": "search engine",
          "fields": ["title","summary"]
        }
      },
      "field_value_factor": {
        "field": "num_reviews",
        "modifier": "log1p",
        "factor": 2
      }
    }
  },
  "_source": ["title", "summary", "publish_date", "num_reviews"]
}

[Results]
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 1.5694137,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "num_reviews": 20,
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 1.4725765,
        "_source": {
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "num_reviews": 23,
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 0.14181662,
        "_source": {
          "summary": "build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
          "num_reviews": 18,
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "2",
        "_score": 0.13297246,
        "_source": {
          "summary": "organize text using approaches such as full-text search, proper name recognition, clustering, tagging, information extraction, and summarization",
          "num_reviews": 12,
          "title": "Taming Text: How to Find, Organize, and Manipulate It",
          "publish_date": "2013-01-24"
        }
      }
    ]
  }
```

>**注1**：我们可以运行一个常规的multi_match查询，并按num_reviews字段排序，但是我们失去了相关性得分的好处。
 **注2**：有许多附加参数可以调整对原始相关性分数 （如“ modifier ”，“ factor ”，“boost_mode”等）的增强效果的程度。
 详见 Elasticsearch guide.





### Function 得分：衰减函数( Function Score: Decay Functions )

离某个值最近得分越高，适用于价格范围、数字字段范围、日期范围。

```json
GET bookdb_index/book/_search
{
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": "search engine",
          "fields": ["title", "summary"]
        }
      },
      "functions": [
        {
          "exp": {
            "publish_date": {
              "origin": "2014-06-15",
              "scale": "30d",
              "offset": "7d"
            }
          }
        }
      ],
      "boost_mode": "replace"
    }
  },
  "_source": ["title", "summary", "publish_date", "num_reviews"]
}

[Results]
  "hits": {
    "total": 4,
    "max_score": 0.22793062,
    "hits": [
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "4",
        "_score": 0.22793062,
        "_source": {
          "summary": "Comprehensive guide to implementing a scalable search engine using Apache Solr",
          "num_reviews": 23,
          "title": "Solr in Action",
          "publish_date": "2014-04-05"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "1",
        "_score": 0.0049215667,
        "_source": {
          "summary": "A distibuted real-time search and analytics engine",
          "num_reviews": 20,
          "title": "Elasticsearch: The Definitive Guide",
          "publish_date": "2015-02-07"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "2",
        "_score": 0.000009612435,
        "_source": {
          "summary": "organize text using approaches such as full-text search, proper name recognition, clustering, tagging, information extraction, and summarization",
          "num_reviews": 12,
          "title": "Taming Text: How to Find, Organize, and Manipulate It",
          "publish_date": "2013-01-24"
        }
      },
      {
        "_index": "bookdb_index",
        "_type": "book",
        "_id": "3",
        "_score": 0.0000049185574,
        "_source": {
          "summary": "build scalable search applications using Elasticsearch without having to do complex low-level programming or understand advanced data science algorithms",
          "num_reviews": 18,
          "title": "Elasticsearch in Action",
          "publish_date": "2015-12-03"
        }
      }
    ]
  }
```





### Function得分：脚本得分（ Function Score: Script Scoring ）

在内置计分功能不符合您需求的情况下，可以选择指定用于评分的Groovy脚本

在我们的示例中，我们要指定一个考虑到publish_date的脚本，然后再决定考虑多少评论。 较新的书籍可能没有这么多的评论，所以他们不应该为此付出“代价”

得分脚本如下所示:

```json
publish_date = doc['publish_date'].value
num_reviews = doc['num_reviews'].value

if (publish_date > Date.parse('yyyy-MM-dd', threshold).getTime()) {
  my_score = Math.log(2.5 + num_reviews)
} else {
  my_score = Math.log(1 + num_reviews)
}
return my_score
```

要动态使用评分脚本，我们使用script_score参数

```json
GET /bookdb_index/book/_search
{
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": "search engine",
          "fields": ["title","summary"]
        }
      },
      "functions": [
        {
          "script_score": {
            "script": {
              "params": {
                "threshold": "2015-07-30"
              },  
              "lang": "groovy", 
              "source": "publish_date = doc['publish_date'].value; num_reviews = doc['num_reviews'].value; if (publish_date > Date.parse('yyyy-MM-dd', threshold).getTime()) { return log(2.5 + num_reviews) }; return log(1 + num_reviews);"
            }
          }
        }
      ]
    }
  },
  "_source": ["title","summary","publish_date", "num_reviews"]
}
```

>**注1**：要使用动态脚本，必须为config / elasticsearch.yml文件中的Elasticsearch实例启用它。 也可以使用已经存储在Elasticsearch服务器上的脚本。 查看 Elasticsearch reference docs 以获取更多信息。
 **注2：** JSON不能包含嵌入的换行符，因此分号用于分隔语句。
 原文作者： by Tim Ojo Aug. 05, 16 · Big Data Zone
 原文地址：[dzone.com/articles/23…](https://link.juejin.im?target=https%3A%2F%2Fdzone.com%2Farticles%2F23-useful-elasticsearch-example-queries)

本文转载https://juejin.im/post/5b7fe4a46fb9a019d92469a9