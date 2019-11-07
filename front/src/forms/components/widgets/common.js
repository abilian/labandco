function add_line() {
  if (!this.model[this.field.name]) {
    this.model[this.field.name] = [];
  }
  this.model[this.field.name].push({});
}

function remove_line(line) {
  const index = this.model[this.field.name].indexOf(line);
  this.model[this.field.name].splice(index, 1);
}

export { add_line, remove_line };
