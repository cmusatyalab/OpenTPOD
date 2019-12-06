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
        proxy("/cvat-ui", {
            target: "http://127.0.0.1:5000"
        })
    );
    app.use(
        proxy("/admin", {
            target: "http://127.0.0.1:5000"
        })
    );
    // don't forward /static yet, as it messes with npm serving
    // app.use(proxy("/static", { target: "http://127.0.0.1:5000" }));
    app.use(proxy("/static/admin", { target: "http://127.0.0.1:5000" }));
    app.use(
        proxy("/static/debug_toolbar", { target: "http://127.0.0.1:5000" })
    );
    app.use(proxy("/static/drf-yasg", { target: "http://127.0.0.1:5000" }));
    app.use(proxy("/static/engine", { target: "http://127.0.0.1:5000" }));
    app.use(
        proxy("/static/rest_framework", { target: "http://127.0.0.1:5000" })
    );
    app.use(proxy("/data", { target: "http://127.0.0.1:5000" }));
};
