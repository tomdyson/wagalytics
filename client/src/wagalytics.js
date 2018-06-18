import moment from 'moment';

$(document).ready(() => {
    const el = document.getElementById('wagalytics-data');
    setup(el.dataset.token, el.dataset.viewId);
});

/**
 * Initialises google analytics and creates the dashboard charts
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
        dashboard.refresh();
    });
}

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
        this.start_date_input = document.getElementById("id_date_from");
        this.end_date_input = document.getElementById("id_date_to");
        this.export_btn = document.getElementById("export-button");
        this.start_date_input.addEventListener('change', () => this.refresh());
        this.end_date_input.addEventListener('change', () => this.refresh());
        $(document.getElementById("export")).submit(() => {
            $(document.getElementById('export-data')).val(JSON.stringify(this.data));
        });

        this.data = {};

        this.tooltips = {
            enabled: true,
            mode: 'label',
            callbacks: {
                title: function (tooltipItems, data) {
                    var idx = tooltipItems[0].index;
                    return 'Title:' + data.labels[idx];//do something with title
                },
                label: function (tooltipItems, data) {
                    return tooltipItems.xLabel;
                }
            }
        }
    }

    setLoading(id) {
        document.getElementById(id).innerHTML = '<i class="icon icon-spinner"></i>';
    }

    /**
     * Setup the charts within the specified date range (last 7 or last 30 days)
     * @param {int} range - use the `ranges` enum to select. (Can be 1 or 2)
     */
    refresh() {
        this.sessionsLineChart();
        this.popularPagesTable();
        this.topReferrersTable();
    }

    /**
     * Query the google API for data within
     * the set range.
     * @param {Object} options Options specifying metrics, dimensions and any
     *  other keys accepted by gapi.
     */
    getQuery(options) {
      $(this.export_btn).prop('disabled', true);
      return query(Object.assign({
          ids: this.view_id,
          'start-date': $(this.start_date_input).val(),
          'end-date': $(this.end_date_input).val()
      }, options));
    }

    /**
     * Create a line chart showing number of sessions per day
     */
    sessionsLineChart() {
        const id = 'sessions-line-chart-container';
        this.setLoading(id);
        this.getQuery(
            {
                dimensions: 'ga:date,ga:nthDay',
                metrics: 'ga:sessions'
            }).then(results => {
                this.data['sessions'] = results.rows;
                $(this.export_btn).prop('disabled', false);
                $(this.export_btn).removeClass('button-longrunning-active');

                var data1 = results.rows.map(row => row[2]);
                var labels = results.rows.map(row => row[0]);
                labels = labels.map(function (label) {
                    return moment(label, 'YYYYMMDD').format('ll');
                });

                var data = {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Sessions',
                            backgroundColor: colors.SALMON_LIGHT,
                            borderColor: colors.SALMON,
                            pointBackgroundColor: colors.SALMON,
                            pointBorderColor: '#fff',
                            data: data1
                        }
                    ]
                };
                new Chart(makeCanvas(id), {
                    type: 'line',
                    data: data,
                    options: {
                        legend: {
                            display: false
                        },
                        scales: {
                            xAxes: [{
                                ticks: {
                                    autoSkip: true,
                                    maxTicksLimit: 4,
                                    maxRotation: 0
                                }
                            }]
                        }
                    }
                });
                //generateLegend('legend-1-container', data.datasets);
            });
    }

    /**
     * Create table showing 25 most popular pages
     */
    popularPagesTable() {
        const id = 'popular-pages-table-container';
        this.setLoading(id);
        const queryData = {
            'metrics': 'ga:pageviews',
            'dimensions': 'ga:hostname,ga:pagePath',
            'sort': '-ga:pageviews',
            'max-results': 25
        };
        this.getQuery(queryData).then(results => {

            // The results contain duplicates for variations in hostname
            // e.g. if someone visit http://mywebsite.com vs http://www.mywebsite.com
            // Here we aggregate these results into single values per page, regardless
            // of hostname
            var i = 0;
            const rows = results.rows;
            const l = rows.length;
            const bars = {};
            for (i; i < l; ++i) {
                const key = rows[i][1]
                if (bars.hasOwnProperty(key)) {
                    bars[key][1] += parseInt(rows[i][2], 10);
                }
                else {
                    bars[key] = [key, parseInt(rows[i][2], 10)];
                }
            }

            this.data['pages'] = Object.values(bars);
            $(this.export_btn).prop('disabled', false);
            $(this.export_btn).removeClass('button-longrunning-active');

            const table = createTable(['Page URL', 'Views'], Object.values(bars));
            const pager = paginateTable(table);
            const container = document.getElementById(id);
            container.innerHTML = '';
            container.appendChild(table);
            $(container).append(pager);
        });
    }

    /**
     * Create table showing 25 top referrers
     */
    topReferrersTable() {
        const id = 'top-referrers-table-container';
        this.setLoading(id);
        const queryData = {
            'metrics': 'ga:pageviews',
            'dimensions': 'ga:fullReferrer',
            'sort': '-ga:pageviews',
            'max-results': 25
        };

        this.getQuery(queryData).then(results => {
            this.data['referrers'] = results.rows;
            $(this.export_btn).prop('disabled', false);
            $(this.export_btn).removeClass('button-longrunning-active');

            const table = createTable(['Source', 'Views'], results.rows);
            const pager = paginateTable(table);
            const container = document.getElementById(id);
            container.innerHTML = '';
            container.appendChild(table);
            $(container).append(pager);
        });
    }
}

/**
 * Create a table
 * @param {*} headings
 * @param {*} rows
 */
function createTable(headings, rows){
    const table = document.createElement('table');
    table.className = 'listing';
    const head = table.createTHead();
    const headerRow = head.insertRow(0);
    let i = 0;
    for (i; i < headings.length; ++i) {
        const heading = headerRow.insertCell(i);
        heading.innerHTML = headings[i];
        heading.className = 'title';
    }
    const body = table.createTBody();
    for (i = 0; i < rows.length; ++i) {
        const rowData = rows[i];
        const row = body.insertRow(i);
        for (let j = 0; j < rowData.length; ++j) {
            row.insertCell(j).innerHTML = rowData[j];
        }
    }
    return table;
}

/**
 * Client side pagination of a table.
 * Table rows are hidden/shown according to the page number
 * @param {*} table
 */
function paginateTable(table) {
    let currentPage = 0;
    const numPerPage = 5;
    const $table = $(table);

    // This is the function which controls display of content
    $table.bind('repaginate', function() {
        $table.find('tbody tr').hide().slice(currentPage * numPerPage, (currentPage + 1) * numPerPage).show();
        let $pager = $table.next();
        if (currentPage <= 0) {
            $pager.find('.prev').addClass('disabled');
        } else {
            $pager.find('.prev').removeClass('disabled');
        }
        if (currentPage >= numPages - 1) {
            $pager.find('.next').addClass('disabled');
        } else {
            $pager.find('.next').removeClass('disabled');
        }
    });
    $table.trigger('repaginate');
    const numRows = $table.find('tbody tr').length;
    const numPages = Math.ceil(numRows / numPerPage);

    // Create the page selector element and add callbacks to handle setting the page
    const $pager = $(`
        <div class="pagination">
            <p>Page <span class="page-num">1</span> of ${numPages}</p>
            <ul>
                <li class="prev disabled">
                    <a class="icon icon-arrow-left" href="#">Previous</a>
                </li>
                <li class="next">
                    <a class="icon icon-arrow-right-after" href="#">Next</a>
                </li>
            </ul>
        </div>`);

    // Previous page click handler
    $pager.find('.prev a').bind('click', event => {
        event.preventDefault();
        currentPage -= 1;
        if (currentPage < 0) {
            currentPage = 0;
        }
        $pager.find('.page-num').text(`${currentPage + 1}`);
        $table.trigger('repaginate');
    });

    // Next page click handler
    $pager.find('.next a').bind('click', event => {
        event.preventDefault();
        currentPage += 1;
        if (currentPage >= numPages) {
            currentPage = numPages - 1;
        }
        $pager.find('.page-num').text(`${currentPage + 1}`);
        $table.trigger('repaginate');
    });
    return $pager;
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
    legend.innerHTML = items.map(function (item) {
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

// Set some global Chart.js defaults.
Chart.defaults.global.animationSteps = 60;
Chart.defaults.global.animationEasing = 'easeInOutQuart';
Chart.defaults.global.responsive = true;
Chart.defaults.global.maintainAspectRatio = false;
