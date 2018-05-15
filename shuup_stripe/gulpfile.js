var gulp = require("gulp");
var less = require("gulp-less");
var concat = require("gulp-concat");
var uglify = require("gulp-uglify");
var plumber = require("gulp-plumber");
var minifycss = require("gulp-cssnano");
var gutil = require("gulp-util");
var PRODUCTION = gutil.env.production || process.env.NODE_ENV === "production";

gulp.task("less", function() {
    return gulp.src(
        ["static_src/admin/less/style.less"])
        .pipe(plumber({}))
        .pipe(less())
        .pipe(concat("shuup_stripe_admin.css"))
        .pipe((PRODUCTION ? minifycss() : gutil.noop()))
        .pipe(gulp.dest("static/shuup_stripe/css/"));
});

gulp.task("js", function() {
    return gulp.src([
        "static_src/admin/js/shuup_stripe.js",

    ])
        .pipe(plumber({}))
        .pipe(concat("shuup_stripe.js"))
        .pipe((PRODUCTION ? uglify() : gutil.noop()))
        .pipe(gulp.dest("static/shuup_stripe/js/"));
});

gulp.task("less:watch", ["less"], function() {
    gulp.watch(["static_src/admin/less/*.less"], ["less"]);
});

gulp.task("js:watch", ["js"], function() {
    gulp.watch(["static_src/js/*.js"], ["js"]);
});


gulp.task("default", ["js", "less"]);

gulp.task("watch", ["js:watch", "less:watch"]);
