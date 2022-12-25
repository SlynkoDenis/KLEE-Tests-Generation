int example(int a, int b, float f) {
    if (f == 1.0f) {
        return a + b / 4;
    }
    if (a == b) {
        return a + b;
    }
    return a - b;
}
