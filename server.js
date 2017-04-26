/**
 * Created by navid on 4/26/17.
 */

var http = require("http");
var express = require("express");
var bodyParser = require('body-parser');
var app = express();
app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({extended: true})); // for parsing application/x-www-form-urlencoded

var address = "localhost";
var port = 3000 ;


app.get("/beacons/" , function (req , res) {
    console.log("someone asking for the beacons");
    reply = [
                {"mac_address" :"DC:78:C7:F3:AD:51" , "x" : 0 ,  "y" : 0} ,
                {"mac_address" :"DC:78:C7:F3:AD:52" , "x" : 0 ,  "y" : 0}
                ];

    res.send(reply);
});


app.post("/beacons/" , function (req  ,res){
        console.log("someone has sent beacon data");
        console.log(JSON.stringify(req.body));
        res.send("GOT IT!!!");
});

//server initiation
var server = app.listen(port, address, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log("Server is listening at http://%s:%s", host, port);
});