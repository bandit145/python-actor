#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <assert.h>
#include <stdlib.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

int main(void) {
	Py_Initialize();
	int py_state = Py_IsInitialized();
	PyObject globals;
	PyObject locals;
	PyObject* data = PyRun_String("def test():\n\tprint('hi')n\n", Py_eval_input, &globals, &locals);
	printf("return data %d\n", data);
	printf("is python initialized main? %c\n", py_state);
	PyThreadState* main_thread = PyThreadState_Get();
	printf("main thread status %d\n", main_thread->interp);
	PyThreadState* new_subint = Py_NewInterpreter();
	printf("new subint thread status %d\n", new_subint->interp);
}