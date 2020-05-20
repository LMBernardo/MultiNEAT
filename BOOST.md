For Windows with MSVC 14.2, use the following commands after running bootstrap.sh

NOTE: b2.exe WILL NOT build boost_numpy unless it detects that numpy is installed (`python -m pip install numpy`)
	  Please make sure that numpy is installed for the version of python used by the build test:
	  `python -c "import sys; sys.stderr = sys.stdout; import numpy; print(numpy.get_include())"`
	  
	  To check test command on your own system, add `--debug-configuration` to commands given below
	  
NOTE: If you get an import module error when attempting to import ._MultiNEAT, you may need to add the Boost
      library directory to your PATH variable (e.g., 'C:\local\boost_1_72_0\stage\lib64-msvc-14.2\lib')

To build boost for x86:
`.\b2.exe address-model=32 toolset=msvc-14.2 threading=multi --build-type=complete stage -j 8`

To build boost for x64:
`.\b2.exe address-model=64 toolset=msvc-14.2 threading=multi --build-type=complete stage -j 8`
