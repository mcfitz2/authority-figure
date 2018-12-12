var passport = require("passport");
var mongoose = require("mongoose");

function ensureAuthenticated(req, res, next) {
	if (req.isAuthenticated())
		return next();
	else
		res.redirect("login");
}
module.exports = function (app, Service) {
	app.post('/login',
		passport.authenticate('local'),
		function (req, res) {
			res.redirect('/');

		});
	app.get("/login", function (req, res) {
		res.render("login");
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
