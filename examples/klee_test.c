#include "klee/klee.h"
int main() {
int arg0;
klee_make_symbolic(&arg0, sizeof(arg0), "arg0 (type int)");int arg1;
klee_make_symbolic(&arg1, sizeof(arg1), "arg1 (type int)");float arg2;
klee_make_symbolic(&arg2, sizeof(arg2), "arg2 (type float)");example(arg0,arg1,arg2);
return 0;
}
