System.register(["./datasource", "./query_ctrl"], function (_export, _context) {
  "use strict";

  var GenericDatasource, GenericDatasourceQueryCtrl;
  return {
    setters: [function (_datasource) {
      GenericDatasource = _datasource.GenericDatasource;
    }, function (_query_ctrl) {
      GenericDatasourceQueryCtrl = _query_ctrl.GenericDatasourceQueryCtrl;
    }],
    execute: function () {
      function _classCallCheck(instance, Constructor) {
        if (!(instance instanceof Constructor)) {
          throw new TypeError("Cannot call a class as a function");
        }
      }

      let GenericConfigCtrl = function GenericConfigCtrl() {
        _classCallCheck(this, GenericConfigCtrl);
      };

      GenericConfigCtrl.templateUrl = 'partials/config.html';

      let GenericQueryOptionsCtrl = function GenericQueryOptionsCtrl() {
        _classCallCheck(this, GenericQueryOptionsCtrl);
      };

      GenericQueryOptionsCtrl.templateUrl = 'partials/query.options.html';

      let GenericAnnotationsQueryCtrl = function GenericAnnotationsQueryCtrl() {
        _classCallCheck(this, GenericAnnotationsQueryCtrl);
      };

      GenericAnnotationsQueryCtrl.templateUrl = 'partials/annotations.editor.html';

      _export("Datasource", GenericDatasource);

      _export("QueryCtrl", GenericDatasourceQueryCtrl);

      _export("ConfigCtrl", GenericConfigCtrl);

      _export("QueryOptionsCtrl", GenericQueryOptionsCtrl);

      _export("AnnotationsQueryCtrl", GenericAnnotationsQueryCtrl);
    }
  };
});
//# sourceMappingURL=module.js.map
