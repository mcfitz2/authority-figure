var fs = require("fs");
var https = require('https');
var express = require("express");
var passport = require("passport");
var session = require("express-session");
var mongoose = require("mongoose");
var flash = require('connect-flash');
var bodyParser = require("body-parser");
var app = express();
app.use(bodyParser.urlencoded({
	extended: true
}));
app.use(session({
	secret: 'keyboard cat'
}));
app.use(passport.initialize());
app.use(passport.session());
app.use(flash());
app.available_services = [
	{name:'fitbit', scope:"activity heartrate location nutrition profile settings sleep social weight", passport_module_name:"passport-fitbit-oauth2", passport_strategy:"FitbitOAuth2Strategy"},
	{name:'strava', scope:"activity:read_all", passport_module_name:"passport-strava", passport_strategy:"Strategy"},
//	{name:'facebook',scope:null, passport_module_name:"passport-fitbit-oauth2", passport_strategy:"Strategy"},
	{name:'twitter', scope:null, passport_module_name:"passport-twitter", passport_strategy:"Strategy"},
//	{name:'foursquare', scope:null, passport_module_name:"passport-fitbit-oauth2", passport_strategy:"Strategy"},},
//	{name:'dropbox', scope:null, passport_module_name:"passport-fitbit-oauth2", passport_strategy:"Strategy"},},
//	{name:'instagram', scope:null, passport_module_name:"passport-fitbit-oauth2", passport_strategy:"Strategy"},},
	{name:'automatic', scope:null, passport_module_name:"passport-automatic", passport_strategy:"Strategy"}
];
app.set('view engine', 'html');
app.engine('html', require('hogan-express'));
app.set('views', __dirname + '/views');
var Service = mongoose.model("Service", new mongoose.Schema({
	name: {
		type: String,
		unique: true
	},
	access_token: String,
	refresh_token: String,
	service_user_id: String,
	user: {
		type: mongoose.Schema.Types.ObjectId,
		ref: 'User', //Edit: I'd put the schema. Silly me.
		required: true,
	}

}));

db = mongoose.connection;
db.on("error", function (err) {
	console.log(err);
});
db.once("open", function () {
	console.log(process.env);

	require("./lib/passport.js")(app, Service);
	require("./lib/routes.js")(app, Service);

//	app.listen(process.env.PORT || 3000);
	https.createServer({
  		key: fs.readFileSync('server.key'),
  		cert: fs.readFileSync('server.cert')
	}, app).listen(process.env.PORT || 5555, () => {
		console.log('Listening...')
	})

});
mongoose.connect(process.env.MONGODB_URI);
