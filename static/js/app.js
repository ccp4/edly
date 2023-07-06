var app = angular.module('app',[]); // ['ngTouch','ngAria','ngRoute']);
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


// Plotly directive
app.directive('linePlot', function () {
  function linkFunc(scope, element, attrs) {
      scope.$watch(attrs.fig, function (new_fig,fig) {
        if (new_fig.data){
          Plotly.newPlot(element[0].id, new_fig.data, new_fig.layout);
          if (element[0].id=='fig1'){
            scope.initPlotly=true
            document.getElementById(element[0].id).on('plotly_click', scope.addRow_tagTable);
            document.getElementById(element[0].id).on('plotly_legendclick', scope.leg_click);
          }
          else if(element[0].id=='fig2'){
            elt = document.getElementById(element[0].id)
            if (elt.layout.title){              
              if (elt.layout.title.text.includes('Iobserved vs Icalc')){
                document.getElementById(element[0].id).on('plotly_click', scope.addRow_tagTable);
              }
            }
          }
        }
      }, true);
  }
  return {
      link: linkFunc
  };
});

app.directive('ngKeyEnter', function() {
  function linkFunc(scope, element, attrs) {
    element.bind("keydown keypress", function(event) {
      if (event.which == 13) {
        scope.$apply(function() {
            scope.$eval(attrs.ngKeyEnter);
        });
      }
    });
  }
  return {
    link:linkFunc
  };
});
