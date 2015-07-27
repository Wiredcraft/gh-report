var RepositoryChart = {};

RepositoryChart = {
    width: 240,
    height: 80,

    margins: {
        left: 100,
        right: 25,
        bottom: 50,
        top: 20
    },

    barHeight: 20,
    labels: ["changes", "created", "commented"],

    // Creates layers for the d3 stack layout based on the dataset
    layers: function(data) {
        var stack = d3.layout.stack();
        return stack(d3.range(data.length).map(
            function(i) {
                var a = [];
                a[0] = {x: RepositoryChart.labels[0], y: data[i].changes, label: data[i].name};
                a[1] = {x: RepositoryChart.labels[1], y: data[i].issues, label: data[i].name};
                a[2] = {x: RepositoryChart.labels[2], y: data[i].issue_comments, label: data[i].name};
                return a;
            }
        ));
    },

    // Gets the SVG chart given the specified chart id
    chart: function (chartId) {
        return d3.select(".chart-" + chartId)
            .attr("width", RepositoryChart.width + RepositoryChart.margins.left + RepositoryChart.margins.right)
            .attr("height", RepositoryChart.height + RepositoryChart.margins.top + RepositoryChart.margins.bottom);
    },

    // Retrieves the JSON data and invokes the chart-drawing process
    setup: function (repositoryData, chartId) {
        d3.json(repositoryData, function(error, data) {
            RepositoryChart.draw(error, data, RepositoryChart.chart(chartId));
        });
    },

    // Creates a tooltip for each section of the bar chart that displays the repository and percentages
    tooltip: d3.tip().attr('class', 'd3-tip')
                .offset([-10, 0])
                .html(function(d) {
                    return "<strong>" + d.label + ":</strong> <span style='color:red'>" + (+d.y.toFixed(2)) + "%</span>";
                }),

    // Turns the raw data into d3 layers
    preprocess: function (data) {
        return RepositoryChart.layers(data.repositories.map(function(x) {
            return {
                changes: x.percent_changes*100,
                issues: x.percent_issues*100,
                issue_comments: x.percent_issue_comments*100,
                name: x.repo
            };
        }));
    },

    // Generates colours based on layers
    colours: function (count) {
        return d3.scale.linear()
            .domain([0, count - 1])
            .range(["#aad", "#556"]);
    },

    // Defines the scale for repository contribution percentages to width on the chart
    horizontalScale: function (maxValue) {
        return d3.scale.linear()
            .domain([0, maxValue])
            .range([0, RepositoryChart.width]);
    },

    // Gets the maximum value for a set of layers
    getMaxValue: function (layers) {
        return d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); });
    },

    buildLayers: function(chart, layers) {
        var maxValue = RepositoryChart.getMaxValue(layers);
        var percentScale = RepositoryChart.horizontalScale(maxValue);

        var ordinalScale = d3.scale.ordinal()
            .domain(RepositoryChart.labels)
            .rangePoints([RepositoryChart.margins.top, RepositoryChart.height], 0.08);

        // Join data to layers
        var layer = chart.selectAll(".layer")
            .data(layers)
            .enter().append("g")
            .attr("class", "layer")
            .style("fill", function(d, i) { return RepositoryChart.colours(layers.length)(i); });

        var yAxis = d3.svg.axis()
          .scale(ordinalScale)
          .orient("left");

        chart.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(100, 20)")
            .call(yAxis);

        // Build rect for each layer
        layer.selectAll("rect")
            .data(function(d) { return d; })
            .enter().append("rect")
            .attr("y", function(d) { return ordinalScale(d.x); })
            .attr("x", function(d) { return percentScale(d.y0); })
            .attr("height", RepositoryChart.barHeight)
            .attr("width", function(d) { return percentScale(d.y); })
            .attr("transform", "translate(100, 10)")
            .on('mouseover', RepositoryChart.tooltip.show)
            .on('mouseout', RepositoryChart.tooltip.hide);
    },

    // 1. Builds layers from the data
    // 2. Creates chart and joins the data layers with the chart
    draw: function (error, data, chart) {
        var layers = RepositoryChart.preprocess(data);
        chart.call(RepositoryChart.tooltip);
        RepositoryChart.buildLayers(chart, layers)
    }
};