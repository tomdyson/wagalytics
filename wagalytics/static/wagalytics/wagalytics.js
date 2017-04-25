
/**
 * The 'public' api - the only function the page needs to know about.
 * @param {*} token_url 
 * @param {*} view_id 
 */
function setup(token_url, view_id) {
    if (!window.google || !window.google.load) {
        var tag = document.createElement('script');
        tag.type = 'text/javascript';
        tag.src = 'https://www.google.com/jsapi';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(tag, s);
    }

    gapi.analytics.ready(function () {
        $.get(token_url, function (data) {
            gapi.analytics.auth.authorize({
                'serverAuth': {
                    'access_token': data
                }
            });
        });

        // Create the dashboard controller
        const dashboard = new Dashboard(view_id);
        dashboard.sessionsLineChart();
        dashboard.popularPagesBar();
        dashboard.topReferrersBar();
    });
}

/**
 * Extend the Embed APIs `gapi.analytics.report.Data` component to
 * return a promise the is fulfilled with the value returned by the API.
 * @param {Object} params The request parameters.
 * @return {Promise} A promise.
 */
function query(params) {
    return new Promise(function (resolve, reject) {
        var data = new gapi.analytics.report.Data({ query: params });
        data.once('success', function (response) { resolve(response); })
            .once('error', function (response) { reject(response); })
            .execute();
    });
}


/**
 * Create a new canvas inside the specified element. Set it to be the width
 * and height of its container.
 * @param {string} id The id attribute of the element to host the canvas.
 * @return {RenderingContext} The 2D canvas context.
 */
function makeCanvas(id) {
    var container = document.getElementById(id);
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');

    container.innerHTML = '';
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    container.appendChild(canvas);

    return ctx;
}

/**
 * Create a visual legend inside the specified element based off of a
 * Chart.js dataset.
 * @param {string} id The id attribute of the element to host the legend.
 * @param {Array.<Object>} items A list of labels and colors for the legend.
 */
function generateLegend(id, items) {
    var legend = document.getElementById(id);
    legend.innerHTML = items.map(function(item) {
        var color = item.color || item.fillColor;
        var label = item.label;
        return '<li><i style="background:' + color + '"></i>' +
            escapeHtml(label) + '</li>';
    }).join('');
}

/**
 * Escapes a potentially unsafe HTML string.
 * @param {string} str An string that may contain HTML entities.
 * @return {string} The HTML-escaped string.
 */
function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

/**
 * The allowable date views for the sessions chart
 */
const ranges = {
    WEEK: 1,
    MONTH: 2
};

/**
 * Wagtails' colour palette
 */
const colors = {
    BLUE: '#71b2d4',
    GREEN: '#189370',
    ORANGE: '#e9b04d',
    RED: '#cd3238',
    SALMON: '#f37e77',
    SALMON_LIGHT: '#fcf2f2',
    TEAL: '#43b1b0',
    TEAL_DARKER: '#358c8b',
    TEAL_DARK: '#246060'
};

/**
 * Sets up the various charts and controls their UI functionality
 */
class Dashboard {
    constructor(view_id) {
        this.view_id = view_id;
    }

    getQueryForRange(range) {
        var now = moment();
        switch (range) {
            case ranges.WEEK:
                return query({
                    'ids': this.view_id,
                    'dimensions': 'ga:date,ga:nthDay',
                    'metrics': 'ga:sessions',
                    'start-date': moment(now).startOf('week').format('YYYY-MM-DD'),
                    'end-date': moment(now).format('YYYY-MM-DD')
                });

            case ranges.MONTH:
                return query({
                    'ids': this.view_id,
                    'dimensions': 'ga:date,ga:nthDay',
                    'metrics': 'ga:sessions',
                    'start-date': moment(now).startOf('month').format('YYYY-MM-DD'),
                    'end-date': moment(now).format('YYYY-MM-DD')
                });

        }
    }

    sessionsLineChart(range = ranges.WEEK) {
        this.getQueryForRange(range).then(results => {
            var data1 = results.rows.map(function (row) { return +row[2]; });
            var labels = results.rows.map(function (row) { return +row[0]; });
            labels = labels.map(function (label) {
                return moment(label, 'YYYYMMDD').format('ddd');
            });

            var data = {
                labels: labels,
                datasets: [
                    {
                        label: 'This Week',
                        fillColor: colors.SALMON_LIGHT,
                        strokeColor: colors.SALMON,
                        pointColor: colors.SALMON,
                        pointStrokeColor: '#fff',
                        data: data1
                    }
                ]
            };
            new Chart(makeCanvas('sessions-line-chart-container')).Line(data);
            //generateLegend('legend-1-container', data.datasets);
        });
    }

    popularPagesBar() {
        const queryData = {
            'ids': this.view_id,
            'start-date': '30daysAgo',
            'end-date': 'today',
            'metrics': 'ga:pageviews',
            'dimensions': 'ga:hostname,ga:pagePath',
            'sort': '-ga:pageviews',
            'max-results': 25
        };
        query(queryData).then(results => {
            // TODO!
            console.log('Popular Pages', results);
        });
    }

    topReferrersBar() {
        const queryData = {
            'ids': this.view_id,
            'start-date': '30daysAgo',
            'end-date': 'today',
            'metrics': 'ga:pageviews',
            'dimensions': 'ga:fullReferrer',
            'sort': '-ga:pageviews',
            'max-results': 25
        };

        query(queryData).then(results => {
            // TODO!
            console.log('Top Referrers', results);
        });
    }
}


// Set some global Chart.js defaults.
Chart.defaults.global.animationSteps = 60;
Chart.defaults.global.animationEasing = 'easeInOutQuart';
Chart.defaults.global.responsive = true;
Chart.defaults.global.maintainAspectRatio = false;
