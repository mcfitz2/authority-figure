var passport = require("passport");
var LocalStrategy = require('passport-local').Strategy,
	BasicStrategy = require('passport-http').BasicStrategy;

var mongoose = require("mongoose");
var User = require("./user.js");
module.exports = function (app, Service) {
	function callback(req, accessToken, refreshToken, profile, done) {

		console.log(profile, req);
		profile.access_token = accessToken;
		profile.refresh_token = refreshToken;
		Service.findOneAndUpdate({
				name: profile.provider,
				user: req.user.id,
			}, {
				access_token: accessToken,
				refresh_token: refreshToken,
				service_user_id: profile.id,
			}, {
				upsert: true
			},
			function (err, service) {
				done(err);
			});
	}
	passport.serializeUser(function (user, done) {
		done(null, user._id);
	});

	passport.deserializeUser(function (id, done) {
		User.findById(id, function (err, user) {
			done(err, user);
		});
	});
	passport.use(new BasicStrategy(
		function (username, password, done) {
			console.log(username, password);
			User.findOne({
				username: username
			}, function (err, user) {
				if (err) {
					console.log(err);
					return done(err);
				}
				if (!user) {
					console.log("no user");
					return done(null, false, {
						message: 'Incorrect username.'
					});
				}
				user.comparePassword(password, function (err, match) {
					if (!match) {
						console.log("badd pass");
						return done(null, false, {
							message: 'Incorrect password.'
						});
					} else {
						console.log("success");
						return done(null, user);
					}
				})

			});
		}
	));
	passport.use(new LocalStrategy(
		function (username, password, done) {
			console.log(username, password);
			User.findOne({
				username: username
			}, function (err, user) {
				if (err) {
					console.log(err);
					return done(err);
				}
				if (!user) {
					console.log("no user");
					return done(null, false, {
						message: 'Incorrect username.'
					});
				}
				user.comparePassword(password, function (err, match) {
					if (!match) {
						console.log("badd pass")
						return done(null, false, {
							message: 'Incorrect password.'
						});
					} else {
						console.log("success");
						return done(null, user);
					}
				})

			});
		}
	));
	for (var i = 0; i<app.available_services.length; i++) {
		var item = app.available_services[i];
		var Strategy = require(item.passport_module_name)[item.passport_strategy];
		if (item.name == "twitter") {
			passport.use(new Strategy({
				consumerKey: process.env[item.name+'_client_id'],
				consumerSecret: process.env[item.name+'_client_secret'],
				callbackURL: process.env[item.name+'_redirect_url'],
				passReqToCallback: true,

			}, callback));
		} else {
			passport.use(new Strategy({
				clientID: process.env[item.name+'_client_id'],
				clientSecret: process.env[item.name+'_client_secret'],
				callbackURL: process.env[item.name+'_redirect_url'],
				passReqToCallback: true,

			}, callback));
		}
}
//	passport.use(new DropboxStrategy({
//		consumerKey: process.env.dropbox_client_id,
//		consumerSecret: process.env.dropbox_client_secret,
//		callbackURL: process.env.dropbox_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
//	passport.use(new StravaStrategy({
//		clientID: process.env.strava_client_id,
//		clientSecret: process.env.strava_client_secret,
//		callbackURL: process.env.strava_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
//	passport.use(new AutomaticStrategy({
//		clientID: process.env.automatic_client_id,
//		clientSecret: process.env.automatic_client_secret,
//		callbackURL: process.env.automatic_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
//	passport.use(new InstagramStrategy({
//		clientID: process.env.instagram_client_id,
//		clientSecret: process.env.instagram_client_secret,
//		callbackURL: process.env.instagram_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
//	passport.use(new FacebookStrategy({
//		clientID: process.env.facebook_client_id,
//		clientSecret: process.env.facebook_client_secret,
//		callbackURL: process.env.facebook_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
//	passport.use(new TwitterStrategy({
//		consumerKey: process.env.twitter_client_id,
//		consumerSecret: process.env.twitter_client_secret,
//		callbackURL: process.env.twitter_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
//	passport.use(new FoursquareStrategy({
//		clientID: process.env.foursquare_client_id,
//		clientSecret: process.env.foursquare_client_secret,
//		callbackURL: process.env.foursquare_callback_url,
//		passReqToCallback: true,
//
//	}, callback));
};
