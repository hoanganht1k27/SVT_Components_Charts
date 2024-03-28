System.register([], function (_export, _context) {
  "use strict";

  return {
    setters: [],
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

      let TableModel = function () {
        function TableModel() {
          _classCallCheck(this, TableModel);

          Object.defineProperty(this, "columns", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "rows", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "type", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          Object.defineProperty(this, "columnMap", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: void 0
          });
          this.columns = [];
          this.columnMap = {};
          this.rows = [];
          this.type = 'table';
        }

        _createClass(TableModel, [{
          key: "sort",
          value: function sort(options) {
            if (options.col === null || this.columns.length <= options.col) {
              return;
            }

            this.rows.sort(function (a, b) {
              a = a[options.col];
              b = b[options.col];

              if (a < b) {
                return -1;
              }

              if (a > b) {
                return 1;
              }

              return 0;
            });
            this.columns[options.col].sort = true;

            if (options.desc) {
              this.rows.reverse();
              this.columns[options.col].desc = true;
            } else {
              this.columns[options.col].desc = false;
            }
          }
        }, {
          key: "addColumn",
          value: function addColumn(col) {
            if (!this.columnMap[col.text]) {
              this.columns.push(col);
              this.columnMap[col.text] = col;
            }
          }
        }]);

        return TableModel;
      }();

      _export("default", TableModel);
    }
  };
});
//# sourceMappingURL=table_model.js.map
