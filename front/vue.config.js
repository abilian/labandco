module.exports = {
  runtimeCompiler: true,
  devServer: {
    disableHostCheck: true,
    proxy: "http://localhost:5000",
    public: "http://localhost:8080",
  },
};
