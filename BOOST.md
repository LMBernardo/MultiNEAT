For Windows with MSVC 14.2, use the following commands after running bootstrap.sh

NOTE: setup.py will use the most up-to-date version of MSVC when determining boost_python and boost_numpy library names
	  For example, if you have both MSVC 14.1 and MSVC 14.2 installed you should build for MSVC 14.2
	  Building for MSVC 14.1 in this case will result in setup.py failure with a message like:
	  "LINK : fatal error LNK1104: cannot open file 'boost_python38-vc142-mt-x32-1_72.lib'"

NOTE: b2.exe WILL NOT build boost_numpy unless it detects that numpy is installed (`python -m pip install numpy`)
	  Please make sure that numpy is installed for the version of python used by the build test:
	  `python -c "import sys; sys.stderr = sys.stdout; import numpy; print(numpy.get_include())"`
	  
	  To check test command on your own system, add `--debug-configuration` to commands given below
	  

To build boost for x86:
`.\b2.exe address-model=32 toolset=msvc-14.2 --stagedir=./stage/lib32-msvc-14.2 --build-dir=build/lib32-msvc-14.2 threading=multi --build-type=complete stage -j 8`

To build boost for x64:
`.\b2.exe address-model=64 toolset=msvc-14.2 --stagedir=./stage/lib64-msvc-14.2 --build-dir=build/lib64-msvc-14.2 threading=multi --build-type=complete stage -j 8`
