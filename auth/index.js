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
	{name:'automatic', scope:null, passport_module_name:"passport-automatic", passport_strategy:"Strategy"},
	{name:'lastfm'},
	{name:'spotify', scope:'user-top-read user-read-email playlist-read-collaborative user-read-birthdate user-library-modify user-follow-read streaming user-read-private user-read-playback-state playlist-modify-public user-follow-modify user-library-read user-modify-playback-state playlist-read-private playlist-modify-private app-remote-control user-read-currently-playing user-read-recently-played', passport_module_name:"passport-spotify", passport_strategy:"Strategy"}
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
var User = mongoose.model("User", require("./lib/user.js"));
db = mongoose.connection;
db.on("error", function (err) {
	console.log(err);
});
db.once("open", function () {
	console.log(process.env);

	require("./lib/passport.js")(app);
	require("./lib/routes.js")(app);

//	app.listen(process.env.PORT || 3000);
	https.createServer({
  		key: fs.readFileSync('server.key'),
  		cert: fs.readFileSync('server.cert')
	}, app).listen(5555, () => {
		console.log('Listening...')
	})

});
mongoose.connect(process.env.MONGODB_URI);
