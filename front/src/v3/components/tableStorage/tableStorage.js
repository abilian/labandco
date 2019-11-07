/**
   Wrappers around localStorage to store and retrieve objects related to a table_demande.

   Set and get functions take a table id as first parameter.

   A commonjs module.

   Goals: modularity and easier unit tests.
**/

/**
 * Return true if localStorage is defined.
 *
 * @return {Boolean}
 * @api public
 */
function isDefined() {
  return typeof Storage !== "undefined";
}

/**
 * Check this table has localStorage info.
 *
 * @return {Boolean}
 * @api public
 */
function hasStorage(table_id) {
  return localStorage.hasOwnProperty(table_id);
}

/**
 * Check this table has localStorage and this key.
 *
 * @return {Boolean}
 * @api public
 */
function hasKey(table_id, key) {
  if (localStorage.hasOwnProperty(table_id)) {
    const storage = JSON.parse(localStorage.getItem(table_id));
    return storage.hasOwnProperty(key);
  }
  return false;
}

/**
 * Store the given object under the given key.
 *
 * @param {String} key
 * @param {any} val Must be JSON.stringify'able.
 * @api public
 */
function set(table_id, key, val) {
  if (typeof Storage !== "undefined") {
    let storage = {};
    if (localStorage.hasOwnProperty(table_id)) {
      storage = JSON.parse(localStorage.getItem(table_id));
    }
    storage[key] = val;
    localStorage.setItem(table_id, JSON.stringify(storage));
  }
}

/**
 * Return the object stored at `key` for the table `table_id`.
 *
 * @param {String} table_id
 * @param {String} key
 * @return {Object}
 * @api public
 */
function get(table_id, key) {
  if (typeof Storage !== "undefined") {
    if (localStorage.hasOwnProperty(table_id)) {
      const storage = JSON.parse(localStorage.getItem(table_id));
      if (storage.hasOwnProperty(key)) {
        return storage[key];
      }
    } else {
      console.log("info: no local storage for component ", table_id);
    }
  }
}

/**
 * Remove the given key from the local storage for table table_id.
 *
 * @param {String} table_id
 * @param {String} key
 * @return {}
 * @api public
 */
function remove(table_id, key) {
  if (typeof Storage !== "undefined") {
    if (localStorage.hasOwnProperty(table_id)) {
      const storage = JSON.parse(localStorage.getItem(table_id));
      if (storage.hasOwnProperty(key)) {
        delete storage[key];
        localStorage.setItem(table_id, JSON.stringify(storage));
      }
    }
  }
}

export const tableStorage = { get, set, remove, hasKey, hasStorage, isDefined };
