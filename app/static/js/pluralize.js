
function pluralize(singular, plural, count){
    if(count < 1){
        throw Error("Count can't be less than 1!");
    }

    if (count == 1){
        return singular;
    } else {
        return count + " " + plural
    }
}