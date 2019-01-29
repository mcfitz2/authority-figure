var mongodb = require('mongodb');
var elevation = require("elevation")
var express = require("express");
var bodyparser = require("body-parser");
var morgan = require('morgan')
const basicAuth = require('express-basic-auth')
const mqtt = require("mqtt")
var app = express();
app.use(bodyparser.json());
app.use(morgan("combined"));
var users = {users:{}}
users.users[process.env.USERNAME] = process.env.PASSWORD;
app.use(basicAuth(users))
var MONGO_URL = process.env.MONGODB_URI;
console.log(MONGO_URL)
mongodb.MongoClient.connect(MONGO_URL, function(err, client) {
    if (err) throw err;
    var mqtt_client  = mqtt.connect(process.env.CLOUDMQTT_URL);

    var db = client.db(process.env.MONGODB_NAME)
    db.collection('owntracks_location_history', function(err, collection) {
        if (err) throw err;
        app.post("/owntracks", (req, res) => {
            var msg = req.body;
            console.log("Received POST request")
            if (msg._type === "location") {
                var event = {};
                event.loc = {};
                event.loc.type = "Point";
                event.loc.coordinates = [parseFloat(msg.lon), parseFloat(msg.lat)];
                event.ts = new Date(parseInt(msg.tst, 10) * 1000);
		elevation.at(event.loc.coordinates[1], event.loc.coordinates[0], (err, meters) => {
			if (err) console.log(err);
			event.alt = meters;
               		collection.update({
                	    ts: event.ts
                	}, event, {
                	    upsert: true
                	}, (err) => {
				var hass_event = {
					longitude:event.loc.coordinates[0],
					latitude: event.loc.coordinates[1],
					timestamp: event.ts,
					alt: event.alt
				}
                                console.log(hass_event)
				mqtt_client.publish("location/micah", JSON.stringify(hass_event));
				res.json({});
			});
		});
            }
        });
	app.listen(process.env.PORT || 5000);
    });
});
