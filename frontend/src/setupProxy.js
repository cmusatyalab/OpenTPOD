const proxy = require("http-proxy-middleware");

module.exports = function(app) {
  app.use(
    proxy("/auth", {
      target: "http://127.0.0.1:5000"
    })
  );
  app.use(
    proxy("/api", {
      target: "http://127.0.0.1:5000"
    })
  );
  app.use(
    proxy("/cvat", {
      target: "http://127.0.0.1:5000"
    })
  );
  // don't forward /static yet, as it messes with npm serving
  //   app.use(proxy("/static", { target: "http://127.0.0.1:5000" }));
};
