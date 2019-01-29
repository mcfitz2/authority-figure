var passport = require("passport");
var mongoose = require("mongoose");
var Service = mongoose.model("Service");
var User = mongoose.model("User");
function ensureAuthenticated(req, res, next) {
	if (req.isAuthenticated())
		return next();
	else
		res.redirect("login");
}
module.exports = function (app) {
	app.post('/login',
		passport.authenticate('local'),
		function (req, res) {
			res.redirect('/');

		});
	app.get("/login", function (req, res) {
		res.render("login");
	});
	app.get("/register", function(req, res) {
		res.render("register");
	});
	app.post("/register", function(req, res) {
		console.log(req.body);
		User.findOne({
                     username: req.body.username
                }, function (err, user) {
	                if (!user) {
        	                var u = new User({
                 	               username: req.body.username,
                                       name: req.body.name,
                                       password: req.body.password,
                                 });
                                 u.save(function (err) {
					if (err) {
						return res.send(err);
					}
                                	console.log("User created", err);
					return res.redirect("/login");
                                 });
			} else {
				return res.redirect("/login");
			}
                });
	});
	app.get("/", ensureAuthenticated, function (req, res) {
		services = app.available_services;
		Service.find({}, function (err, saved) {
			for (var i = 0; i < saved.length; i++) {
				for (var j = 0; j < services.length; j++) {
					if (saved[i].name == services[j].name) {
						services[j].has_token = true;
					}
				}
			}
			console.log(services);
			res.locals.services = services;
			res.render("index");
		});

	});
	for (var i = 0; i < app.available_services.length; i++) {
		var item = app.available_services[i];
		var options = {}
                if (item.name == "lastfm") {
                        continue
                }
		if (item.scope) {
			options.scope = item.scope;
		}
	console.log('/auth/'+item.name);
	app.get('/auth/'+item.name, ensureAuthenticated, passport.authorize(item.name, options));

	app.get('/auth/'+item.name+'/callback', ensureAuthenticated,
		passport.authorize(item.name, {
			failureRedirect: '/'
		}),
		function (req, res) {
			res.redirect('/');
		});
	}
        app.get('/auth/lastfm', ensureAuthenticated, (req, res) => {
                res.render("lastfm")
        });
        app.post('/auth/lastfm/callback', ensureAuthenticated, (req, res) => {
                Service.findOneAndUpdate({
                                name: 'lastfm',
                                user: req.user.id,
                        }, {
                                access_token: null,
                                refresh_token: null,
                                service_user_id: req.body.lastfm_username,
                        }, {
                                upsert: true
                        },
                        function (err, service) {
                             if (err) {
                                res.send(500)
                                } else {
                                res.redirect("/")
                                }
                        });
        });
	app.get("/get/:service", passport.authenticate("basic"), function (req, res) {
		Service.findOne({
			name: req.params.service,
			user: req.user._id,
		}, function (err, service) {
			if (service) {
				var response = {
					client_id: process.env[req.params.service + "_client_id"],
					client_secret: process.env[req.params.service + "_client_secret"],
					callback_url: process.env[req.params.service + "_callback_url"],
					name: service.name,
					access_token: service.access_token,
					refresh_token: service.refresh_token,
					service_user_id: service.service_user_id,
					user: service.user,
				};

				console.log(response);
				res.json(response);
			} else {
				res.sendStatus(404);
			}
		});
	});
};
