/*
 * Возврашает строковое представление числа integer,
 * дополненное слева нулям до длины length
 */
Number.prototype.zfill = function(length) { 
    var str = this.toString();
    if (str.length < length) {
        for(var i = 0; i < length - str.length; i++) str = '0' + str
    }

    return str;
};

Array.prototype._clone = function() {
    var ar = [];
    for(var i = 0; i < this.length; i++) {
        ar.push(this[i]);
    }
    return ar;
}
