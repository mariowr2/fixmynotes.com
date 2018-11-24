VENV_LIB = virtual_env/lib/python2.7
VENV_CV2 = $(VENV_LIB)/cv2.so

#find cv2 library for the global python installation
GLOBAL_CV2 := $(shell /usr/bin/python -c 'import cv2; print(cv2)' | awk '{print $$4}' | sed s:"['>]":"":g)

#link global cv2 library file inside the virtual environment
$(VENV_CV2): $(GLOBAL_CV2) virtual_env
	cp $(GLOBAL_CV2) $@

#linke the .so into the virtual env?
virtual_env: requirements.txt
	test -d virtual_env || virtualenv virtual_env
	. virtual_env/bin/activate && pip install -r requirements.txt

# test if cv2 can be imported inside the virtual env
test: $(VENV_CV2)
	. virtual_env/bin/activate && python -c 'import cv2; print(cv2)'

clean:
	rm -rf virtual_env
