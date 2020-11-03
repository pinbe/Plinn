export function readCookie(name: string) {
    // from w3schools.com
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(nameEQ) !== -1) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}
