function make_bond_graph(data_file) {

var margin = {top:20, right:20, bottom:20, left:40}
var width = 500 - margin.right;
var height = 500 - margin.top - margin.bottom

var svg = d3.select("#id_bond_pp_graph")
            .append("svg")
            .attr("height", height + margin.top + margin.bottom)
            .attr("width", width + margin.left + margin.right)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("text") 
     .attr("class", "x label")
     .attr("x", width)
     .attr("y", height - 6)
     .style("text-anchor", "end")
     .text("Distance");

  svg.append("text")
     .attr("class", "y label")
     .attr("text-anchor", "end")
     .attr("y", 6)
     .attr("dy", ".75em")
     .attr("transform", "rotate(-90)")
     .attr("Perturbation Propensity")

  d3.csv(data_file, function(error, data) {
  if (error) {
     console.log(error);
  } else {
     console.log(data);

      var dataset = data.map(function(d) {return [d['bond_name'], +d['distance'], +d['pp_adjusted'], d['atom1'], d['atom2']];});
     makeScatterPlot(dataset);
         }
  });
    
  function makeScatterPlot(dataset) {
 
  var xScale = d3.scale.linear()
                       .domain([0, d3.max(dataset, function(d) {return d[1];})])
                       .range([0, width]);
  
  var yScale = d3.scale.linear()
                       .domain([0, d3.max(dataset, function(d) { return d[2]; })])
                       .range([height, 0]);

  var xAxis = d3.svg.axis()
                    .scale(xScale)
                    .orient("bottom")

  var yAxis = d3.svg.axis()
                    .scale(yScale)
                    .orient("left")

  svg.append("g")
     .attr("class", "axis")
     .attr("transform", "translate(0," + height + ")")
     .call(xAxis);

  svg.append("g")
     .attr("class", "axis")
     .call(yAxis);

  var circles = svg.append("g")
                   .attr("id", "circles")
                   .attr("clip-path", "url(#chart_area)")
                   .selectAll("circle")
                   .data(dataset)
                   .enter()
                   .append("circle")
                   .on("mouseover", function(d) { 
                     d3.select(this)
                       .attr("fill", "red");
                   })
                   .on("mouseout", function(d) {
                     d3.select(this)
                       .attr("fill", "blue");
                   })
                   .on("click", function(d) {showBond(d);});
                   
                    

  circles.attr("cx", function(d) {
              return xScale(d[1]);
          })
         .attr("cy", function(d) {
              return yScale(d[2]);
          })
         .attr("r", 7)
         .attr("fill", "blue");

  circles.append("title")
      .text(function(d) {return d[0]; });

}
}
