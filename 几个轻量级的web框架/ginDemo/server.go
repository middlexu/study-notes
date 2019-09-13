package main

import "github.com/gin-gonic/gin"
import "fmt"

func main() {
	r := gin.Default()
	// # 路径参数 查询字符串 表单 json
	// # 纯文本 json 
	r.Static("/static","./static")
	
	r.GET("/", func(c *gin.Context) {
		fmt.Println(c.GetHeader("a"))
		c.Header("k","l")
		c.String(200,"hello gin")
	})
	r.GET("/path/:id",func(c *gin.Context) {
		c.String(200,c.Param("id"))
	})
	r.GET("/querystring",func(c *gin.Context) {
		c.String(200,c.Query("username"))
	})
	r.POST("/form",func(c *gin.Context) {
		c.String(200,c.PostForm("username"))
	})
	r.POST("/json",func(c *gin.Context) {
		var amap interface{}
		c.BindJSON(&amap)
		c.JSON(200,amap)
	})
	r.Run(":3003")
}
