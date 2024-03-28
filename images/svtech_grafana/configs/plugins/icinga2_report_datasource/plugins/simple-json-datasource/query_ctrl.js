System.register(["app/plugins/sdk", "./css/query-editor.css!"], function (_export, _context) {
  "use strict";

  var QueryCtrl;
  return {
    setters: [function (_appPluginsSdk) {
      QueryCtrl = _appPluginsSdk.QueryCtrl;
    }, function (_cssQueryEditorCss) {}],
    execute: function () {
      function _classCallCheck(instance, Constructor) {
        if (!(instance instanceof Constructor)) {
          throw new TypeError("Cannot call a class as a function");
        }
      }

      function _defineProperties(target, props) {
        for (var i = 0; i < props.length; i++) {
          var descriptor = props[i];
          descriptor.enumerable = descriptor.enumerable || false;
          descriptor.configurable = true;
          if ("value" in descriptor) descriptor.writable = true;
          Object.defineProperty(target, descriptor.key, descriptor);
        }
      }

      function _createClass(Constructor, protoProps, staticProps) {
        if (protoProps) _defineProperties(Constructor.prototype, protoProps);
        if (staticProps) _defineProperties(Constructor, staticProps);
        return Constructor;
      }

      function _possibleConstructorReturn(self, call) {
        if (call && (typeof call === "object" || typeof call === "function")) {
          return call;
        }

        if (!self) {
          throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
        }

        return self;
      }

      function _inherits(subClass, superClass) {
        if (typeof superClass !== "function" && superClass !== null) {
          throw new TypeError("Super expression must either be null or a function");
        }

        subClass.prototype = Object.create(superClass && superClass.prototype, {
          constructor: {
            value: subClass,
            enumerable: false,
            writable: true,
            configurable: true
          }
        });
        if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass;
      }

      let GenericDatasourceQueryCtrl = function (_QueryCtrl) {
        _inherits(GenericDatasourceQueryCtrl, _QueryCtrl);

        function GenericDatasourceQueryCtrl($scope, $injector) {
          var _this;

          _classCallCheck(this, GenericDatasourceQueryCtrl);

          _this = _possibleConstructorReturn(this, (GenericDatasourceQueryCtrl.__proto__ || Object.getPrototypeOf(GenericDatasourceQueryCtrl)).call(this, $scope, $injector));
          _this.scope = $scope;
          _this.target.target = _this.target.target || 'select metric';
          _this.target.type = _this.target.type || 'timeserie';
          return _this;
        }

        _createClass(GenericDatasourceQueryCtrl, [{
          key: "getOptions",
          value: function getOptions(query) {
            return this.datasource.metricFindQuery(query || '');
          }
        }, {
          key: "toggleEditorMode",
          value: function toggleEditorMode() {
            this.target.rawQuery = !this.target.rawQuery;
          }
        }, {
          key: "onChangeInternal",
          value: function onChangeInternal() {
            this.panelCtrl.refresh(); // Asks the panel to refresh data.
          }
        }]);

        return GenericDatasourceQueryCtrl;
      }(QueryCtrl);

      _export("GenericDatasourceQueryCtrl", GenericDatasourceQueryCtrl);

      GenericDatasourceQueryCtrl.templateUrl = 'partials/query.editor.html';
    }
  };
});
//# sourceMappingURL=query_ctrl.js.map
