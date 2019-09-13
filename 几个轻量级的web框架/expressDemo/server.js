var express =require('express');
var app = express();
app.use(express.urlencoded({extended:false}))
app.use(express.json())

// 设置静态资源目录
app.use("/static",express.static("static"))

app.get('/',function(req,res){
    console.log(req.headers.a)
    res.header("b","c");  // 设置响应头
    res.send("hello express");
});

// http://localhost:3001/path/1000
app.get('/path/:id',function(req,res){
    console.log(req.params.id)
    res.send(req.params.id)
})

// http://localhost:3001/querystring?name=zhangsan&age=18
app.get('/querystring',function(req,res){
    console.log(req.query)
    res.send(req.query.name)
})

app.post('/form',function(req,res){
    console.log(req.body)  // req.body 接收来自表格的数据
    res.send(req.body.username)
})

app.post('/json',function(req,res){
    console.log(req.body)
    res.json({"a":12,b:"jjjj"})
})
app.listen(3001);