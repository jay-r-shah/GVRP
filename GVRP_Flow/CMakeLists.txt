#-------------------------------------------------------------
#           CMakeLists.txt file for GUROBI and CPLEX
#                     copyright (c) 2017
#                 NIKOS LAPPAS (nlappas@cmu.edu)
#          ANIRUDH SUBRAMANYAM (asubramanyam@cmu.edu)
#                  CARNEGIE MELLON UNIVERSITY
# version 0.4.0
#-------------------------------------------------------------

# PLATFORMS SUPPORTED: WIN64, LINUX64

#---------
# LINUX64
#---------
# 1) in LINUX place this CMakeLists.txt file next to your project src (.cpp, .c) files
#
# 2) make a new folder inside the main project directory and run the command:
#    $ cmake Unix Makefiles -DCMAKE_BUILD_TYPE=Debug <path_to_CMakeLists.txt>
#    to make your own makefile. (use the option -DCMAKE_BUILD_TYPE=Release for RELEASE mode)
#
#    For example, if your project is organized as "projectdir/src" and "projectdir/inc",
#    then place CMakeLists.txt inside "projectdir/src"
#    and make another folder "projectdir/build" and run the above command from inside this folder
#
# 3) execute the make command to create the executable/library (within the above folder)
#
#
#---------
# WIN64
#---------
#
#  -> MS VISUAL STUDIO 2017 supports CMakeLists.txt out of the box, via opening the folder containing it. 
#    (link: https://blogs.msdn.microsoft.com/vcblog/2016/10/05/cmake-support-in-visual-studio/).
#  ! [ Caution for Win7/8 Users: "Windows Universal CRT SDK" and "Windows8.1 SDK" have to be checked in the tab
#      "Individual Components" during the installation of Visual Studio 2017. Failure to do so, will lead to no
#      detection of the C++ compiler by the CMAKE ]
#
#  Follow the prescribed steps to compile and run:
# 1) Open the root folder of your project that contains the main CMakeLists.txt with the open folder function of VS
#
# 2) Go to menu CMake->Change Cmake Settings->CMakeLists.txt. A CMakeSettings.json will open.
#
# 3) In the CMakeSettings.json apply the following changes:
#    a. for the "x64-Debug" part, change the "buildRoot" to the folder that you want the .exe to be generated (e.g. "${workspaceRoot}\\mydebugbuild")
#       and set "cmakeCommandArgs": "-DCMAKE_BUILD_TYPE=Debug"
#    b. for the "x64-Release part,  change the "buildRoot" to the folder that you want the .exe to be generated (e.g. "${workspaceRoot}\\myreleasebuild")
#       and set "cmakeCommandArgs": "-DCMAKE_BUILD_TYPE=Release"
# 4) If you want to run within VS your code go to menu CMake->Debug and launch settings->{yourExecutableName}. A launch.vs.json file will open.
#
# 5) In the launch.vs.json apply the following changes:
#    a. set the directory you want the executable file to be executed from e.g. the root directory: "currentDir": "${workspaceRoot}"
#    b. set any command line arguments that your program requires to run by adding: "args": ["arg1 arg2 arg3"]
#
# 6) Select the proper mode from the toolbar dropdown e.g. x64-Release, and press the green play button to compile and run 
#    
#  -> MS VISUAL STUDIO 2013,2015 are supported through the cmake facility for windows. 
#
#  Follow the prescribed steps to compile and run:
# 1) install cmake at least version 2.8 (link: https://cmake.org/download/)
#    and add it to the system path
#
# 2) make a new folder inside the main project directory and from the command line run the command:
#    cmake  -DCMAKE_BUILD_TYPE=Debug <path_to_CMakeLists.txt> -G "Visual Studio 14 Win64"
#    where 12 is the version of visual studio installed (12 -> VS2013, 14 -> VS2015)
#    (use the option -DCMAKE_BUILD_TYPE=Release for RELEASE mode)
#
# 3) open the solution file (.sln) with visual studio and compile it from the IDE.
#
# 4) check in VS options: solution/properties/C C++/Code Generation/ RuntimeLibrary.
#    This script utilizes Multi-threaded Dynamic Libraries (/MD, /MDd).
#    CPLEX does not provide static libraries in Windows.
#    Finally in the IDE of Visual studio make sure that the corresponding build type is selected (debug/release)


cmake_minimum_required(VERSION 2.8)
###########################################################################################
#           BASIC USER CONFIGURATION MODULE

#NOTE: For directories different than the residing directory of CMakeLists.txt
#      please provide the full directory and not a relative one.
#      e.g. /home/user/project/headers instead of ../headers

project(GVRPFlow)

# Designate cluster: "yes", "no"
set(CLUSTER no)

# Enable all compiler warnings (-Wall, -Wextra): "yes", "no"
set(ENABLE_ALL_WARNINGS no)

# Treat compiler warnings as errors (-Werror): "yes", "no"
set(ENABLE_WERROR no)

# Enable MILP solver: "gurobi", "cplex"
set(SOLVER cplex)

# Specify source files (.cpp, .c) can also include all of the files of a directory eg. directory/*.cpp
# Here the source files are read line by line from text file sourceFiles.proj (make sure there are no trailing
# spaces). Extra files can be appended in the MY_SOURCE_FILES variable
file(STRINGS sourceFiles.proj PROJECTSRCS)
set(MY_SOURCE_FILES
    ${PROJECTSRCS}
)

# Specify custom header directories (else let the keyword "DEFAULT")
# unit testing:  /home/nlappas/Documents/Catch-master/single_include/
set(HDRDIR
    DEFAULT
)

# Specify custom libraries (LINUX-> without "lib" prefix  and without .a postfix (else let the keyword "DEFAULT")
set(MYLIBRARIES
    DEFAULT
)

# Specify paths to above custom libraries (*.a) (else let the keyword "DEFAULT")
set(LIBDIR
    DEFAULT
)

# Choose whether to link the BOOST library: "yes", "no" (Do not choose "yes" if the BOOST library is header-only)
set(ADD_BOOST no)

# Choose whether to link the CONAN package manager: "yes", "no"
set(ADD_CONAN no)

# Specify if the target is executable or library: "exe", "lib", "both", "test".
# Unit tests should be written in test.cpp. If "test" flag is applied, the main.cpp will not be compiled,
# since test.cpp should contain its own main().
# Unit testing provided by Catch https://github.com/philsquared/Catch
set(MYTARGET exe)

# Specify name of executable / library
set(EXEC
    run.exe
)

# Specify additional flags in brackets e.g. "-pg -v" (GCC only) (else let the keyword "DEFAULT")
set(ADDITIONAL_GCC_COMPILER_FLAGS
        DEFAULT
)

# Specify additional flags in brackets e.g. "/Md" (VS only) (else let the keyword "DEFAULT")
set(ADDITIONAL_VS_COMPILER_FLAGS
        DEFAULT
)


# List of useful GCC compiler flags
# -pg               : Enable Profiling
# -v                : Enable Verbose Mode
# -D_GLIBCXX_DEBUG  : Enable STD library bound checking (confuses CLION real-time resolution)
# -E                : Enable output of preprocessor
# -fopenmp          : Enable OpenMP #pragma's


###########################################################################################
#                      DIRECTORY CONFIGURATION MODULE

# set the compiler directory if not the default
# In our CENTOS7 distro the latest gcc is not in the default directory
set(COMPILER_DIR_LINUX /usr/local/bin/g++)


set(WINDOWS_TOOLCHAIN VS) # "VS" or "GCC"
if(${WINDOWS_TOOLCHAIN} STREQUAL "GCC")
set(COMPILER_DIR_WINDOWS C:\\TDM-GCC-64\\bin\\g++)
elseif(${WINDOWS_TOOLCHAIN} STREQUAL "VS")
set(COMPILER_DIR_WINDOWS DEFAULT)
else()
message("INVALID TOOLCHAIN")
endif()

# NOTE: This solver path configuration can only accomondate only minor solver releases
#       Major releases usually lead to the introduction of new libraries (with new names)
#       and as a result these have to be explicitly specified in the target_link_libraries
#       portion of this script

#set the CPLEX DIRECTORY (SUPPORTS ONLY 12.7.x)
set(CPLEX_DIR_LINUX /opt/ibm/ILOG/CPLEX_Studio1271)
set(CPLEX_DIR_WINDOWS C:\\Program\ Files\\IBM\\ILOG\\CPLEX_Studio1271)

#set the GUROBI DIRECTORY (SUPPORTS ONLY 7.x)
set(GUROBI_DIR_LINUX /opt/gurobi702/linux64)
set(GUROBI_DIR_WINDOWS C:\\gurobi702\\win64)

#(optional) Set a subproject directory with additional source files
set(SUBPROJECT_DIR DEFAULT)

# Double check that the solver libraries versions match your selected solver version
# For CPLEX:  Check comments "(CPLEX {1-4}/4)" 
# For GUROBI: Check comments "(GUROBI {1-6}/6)"

##########################################################################################
#                  END OF USER CONFIGURATION MODULES
##########################################################################################
























########################################################################################################################
#           DO NOT CHANGE THE FOLLOWING CODE!


# DETECT PLATFORM (LINUX, WINDOWS) - NOTE: Darwin platform not supported in this script yet.
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
set(mySystem "LINUX")
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
set(mySystem "WINDOWS")
else()
message( FATAL_ERROR "ONLY WINDOWS AND LINUX ARE SUPPORTED AT THIS TIME")
endif()
##----------------------------------------------------------------------------------------------------------------------


# MACRO DEFINITIONS
if(${mySystem} STREQUAL "LINUX")
add_definitions(-DUNIX -DLINUX)
endif()

if(${mySystem} STREQUAL "WINDOWS")
add_definitions(-DWIN64 -DWINDOWS)
endif()

if(${CLUSTER} STREQUAL yes)
add_definitions(-DCLUSTER)
endif()
##----------------------------------------------------------------------------------------------------------------------

# SET COMPILER DIRECTORY
if(${mySystem} STREQUAL "LINUX")
if(NOT "${COMPILER_DIR_LINUX}" STREQUAL "DEFAULT")
set(CMAKE_CXX_COMPILER ${COMPILER_DIR_LINUX})
endif()
endif()
if(${mySystem} STREQUAL "WINDOWS")
if(NOT "${COMPILER_DIR_WINDOWS}" STREQUAL "DEFAULT")
set(CMAKE_CXX_COMPILER ${COMPILER_DIR_WINDOWS})
endif()
endif()
##----------------------------------------------------------------------------------------------------------------------

# SET COMPILER FLAGS
set(COMP_FLAGS_BASIC_DEBUG " -g -std=c++14 -m64 -O0 -pthread -D_GLIBCXX_DEBUG")
set(COMP_FLAGS_BASIC_RESEASE " -std=c++14 -m64 -O2 -pthread -DNDEBUG")
set(COMP_FLAGS_BASIC_VS_DEBUG " /Od /MDd")
set(COMP_FLAGS_BASIC_VS_RESEASE " /O2 /MD /DNDEBUG")


if(${ENABLE_ALL_WARNINGS} STREQUAL "yes")
set(COMP_FLAGS_BASIC_DEBUG "${COMP_FLAGS_BASIC_DEBUG} -Wall -Wextra")
set(COMP_FLAGS_BASIC_RESEASE "${COMP_FLAGS_BASIC_RESEASE} -Wall -Wextra")
set(COMP_FLAGS_BASIC_VS_DEBUG "${COMP_FLAGS_BASIC_VS_DEBUG} /Wall /W4")
set(COMP_FLAGS_BASIC_VS_RESEASE "${COMP_FLAGS_BASIC_VS_RESEASE} /Wall /W4")
endif()

if(${ENABLE_WERROR} STREQUAL "yes")
set(COMP_FLAGS_BASIC_DEBUG "${COMP_FLAGS_BASIC_DEBUG} -Werror")
set(COMP_FLAGS_BASIC_RESEASE "${COMP_FLAGS_BASIC_RESEASE} -Werror")
set(COMP_FLAGS_BASIC_VS_DEBUG "${COMP_FLAGS_BASIC_VS_DEBUG} /WX")
set(COMP_FLAGS_BASIC_VS_RESEASE "${COMP_FLAGS_BASIC_VS_RESEASE} /WX")
endif()

if(${SOLVER} STREQUAL "gurobi")
set(COMP_FLAGS_BASIC_DEBUG "${COMP_FLAGS_BASIC_DEBUG} -D_GLIBCXX_USE_CXX11_ABI=0")
set(COMP_FLAGS_BASIC_RESEASE "${COMP_FLAGS_BASIC_RESEASE} -D_GLIBCXX_USE_CXX11_ABI=0")
elseif(${SOLVER} STREQUAL "cplex")
set(COMP_FLAGS_BASIC_DEBUG "${COMP_FLAGS_BASIC_DEBUG} -DIL_STD -fPIC -fno-strict-aliasing -fexceptions")
set(COMP_FLAGS_BASIC_RESEASE "${COMP_FLAGS_BASIC_RESEASE} -DIL_STD -fPIC -fno-strict-aliasing -fexceptions")
set(COMP_FLAGS_BASIC_VS_DEBUG "${COMP_FLAGS_BASIC_VS_DEBUG} /Zi /DIL_STD")
set(COMP_FLAGS_BASIC_VS_RESEASE "${COMP_FLAGS_BASIC_VS_RESEASE} /DIL_STD")
endif()

if( (${mySystem} STREQUAL "LINUX") OR (${mySystem} STREQUAL "WINDOWS" AND ${WINDOWS_TOOLCHAIN} STREQUAL "GCC") )
if(NOT "${ADDITIONAL_GCC_COMPILER_FLAGS}" STREQUAL "DEFAULT")
foreach(flag ${ADDITIONAL_GCC_COMPILER_FLAGS})
set(COMP_FLAGS_BASIC_DEBUG "${COMP_FLAGS_BASIC_DEBUG} ${flag}")
set(COMP_FLAGS_BASIC_RESEASE "${COMP_FLAGS_BASIC_RESEASE} ${flag}")
endforeach(flag)
endif()
else()
if(NOT "${ADDITIONAL_VS_COMPILER_FLAGS}" STREQUAL "DEFAULT")
foreach(flag ${ADDITIONAL_VS_COMPILER_FLAGS})
set(COMP_FLAGS_BASIC_DEBUG "${COMP_FLAGS_BASIC_DEBUG} ${flag}")
set(COMP_FLAGS_BASIC_RESEASE "${COMP_FLAGS_BASIC_RESEASE} ${flag}")
endforeach(flag)
endif()
endif()

set(COMP_FLAGS_DEBUG ${COMP_FLAGS_BASIC_DEBUG})
set(COMP_FLAGS_RELEASE ${COMP_FLAGS_BASIC_RESEASE})
set(COMP_FLAGS_VS_DEBUG ${COMP_FLAGS_BASIC_VS_DEBUG})
set(COMP_FLAGS_VS_RESEASE ${COMP_FLAGS_BASIC_VS_RESEASE})


if(${mySystem} STREQUAL "LINUX")
set(CMAKE_CXX_FLAGS_DEBUG   "${CMAKE_CXX_FLAGS} ${COMP_FLAGS_DEBUG}")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} ${COMP_FLAGS_RELEASE}")
elseif(${mySystem} STREQUAL "WINDOWS" AND ${WINDOWS_TOOLCHAIN} STREQUAL "VS")
set(CMAKE_CXX_FLAGS_DEBUG   "${CMAKE_CXX_FLAGS} ${COMP_FLAGS_VS_DEBUG}")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} ${COMP_FLAGS_VS_RESEASE}")
STRING(REPLACE "DWIN32" "DWIN64" CMAKE_CXX_FLAGS_DEBUG ${CMAKE_CXX_FLAGS_DEBUG})
STRING(REPLACE "DWIN32" "DWIN64" CMAKE_CXX_FLAGS_RELEASE ${CMAKE_CXX_FLAGS_RELEASE})
elseif(${mySystem} STREQUAL "WINDOWS" AND ${WINDOWS_TOOLCHAIN} STREQUAL "GCC")
set(CMAKE_CXX_FLAGS_DEBUG   "${CMAKE_CXX_FLAGS} ${COMP_FLAGS_DEBUG}")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} ${COMP_FLAGS_RELEASE}")
else()
message( INVALID OS )
endif()
##----------------------------------------------------------------------------------------------------------------------


# SET INCLUDE DIRECTORIES (.h .hpp)
if(${mySystem} STREQUAL "LINUX" AND ${SOLVER} STREQUAL "gurobi")
include_directories(${EXEC}   ${GUROBI_DIR_LINUX}/include)
elseif(${mySystem} STREQUAL "WINDOWS" AND ${SOLVER} STREQUAL "gurobi")
include_directories(${EXEC}   ${GUROBI_DIR_WINDOWS}\\include)
elseif(${mySystem} STREQUAL "LINUX" AND ${SOLVER} STREQUAL "cplex")
include_directories(${EXEC}   ${CPLEX_DIR_LINUX}/cplex/include
${CPLEX_DIR_LINUX}/concert/include)
elseif(${mySystem} STREQUAL "WINDOWS" AND ${SOLVER} STREQUAL "cplex")
include_directories(${EXEC}   ${CPLEX_DIR_WINDOWS}\\cplex\\include
${CPLEX_DIR_WINDOWS}\\concert\\include)
else()
message( FATAL_ERROR "INVALID SOLVER OS COMBINATION" )
endif()


# INCLUDE THE CUSTOM INC DIRECTORIES IF DEFINED
if(NOT "${HDRDIR}" STREQUAL "DEFAULT")
foreach(item ${HDRDIR})
include_directories(${EXEX}  ${item})
endforeach(item)
endif()

# INCLUDE BOOST
if(${ADD_BOOST} STREQUAL "yes")
set(Boost_USE_STATIC_LIBS OFF)
set(Boost_USE_MULTITHREADED ON)
set(Boost_USE_STATIC_RUNTIME OFF)
find_package(Boost 1.50.0 REQUIRED)
if (Boost_FOUND)
message("FOUND BOOST")
include_directories(${EXEC}  ${Boost_INCLUDE_DIR})
endif()
elseif(${ADD_BOOST} STREQUAL "no")
else()
message( FATAL_ERROR "INVALID_BOOST_OPTION")
endif()


# INCLUDE CONAN
if(${ADD_CONAN} STREQUAL "yes")
    include(./conanbuildinfo.cmake)
    conan_basic_setup()
endif()

# INCLUDE SUBPROJECTS
if(NOT "${SUBPROJECT_DIR}" STREQUAL "DEFAULT")
add_subdirectory(${SUBPROJECT_DIR})
endif()
##----------------------------------------------------------------------------------------------------------------------



# SET SOURCE_FILES
set(SOURCE_FILES ${MY_SOURCE_FILES})
##----------------------------------------------------------------------------------------------------------------------

# SET LINK DIRECTORIES
if(${mySystem} STREQUAL "LINUX" AND ${SOLVER} STREQUAL "gurobi")
link_directories(${GUROBI_DIR_LINUX}/lib)
elseif(${mySystem} STREQUAL "WINDOWS" AND ${SOLVER} STREQUAL "gurobi")
link_directories(${GUROBI_DIR_WINDOWS}\\lib)
elseif(${mySystem} STREQUAL "LINUX" AND ${SOLVER} STREQUAL "cplex")
link_directories(${CPLEX_DIR_LINUX}/cplex/lib/x86-64_linux/static_pic
${CPLEX_DIR_LINUX}/concert/lib/x86-64_linux/static_pic)
elseif(${mySystem} STREQUAL "WINDOWS" AND ${SOLVER} STREQUAL "cplex")
if(${CMAKE_BUILD_TYPE} STREQUAL "Release")
link_directories(${CPLEX_DIR_WINDOWS}\\cplex\\lib\\x64_windows_vs2015\\stat_mda   #### VISUAL STUDIO VERSION (CPLEX 1/4) ####
${CPLEX_DIR_WINDOWS}\\concert\\lib\\x64_windows_vs2015\\stat_mda)
else() #Debug mode by default
link_directories(${CPLEX_DIR_WINDOWS}\\cplex\\lib\\x64_windows_vs2015\\stat_mdd   #### VISUAL STUDIO VERSION (CPLEX 2/4) ####
${CPLEX_DIR_WINDOWS}\\concert\\lib\\x64_windows_vs2015\\stat_mdd)
endif()
else()
message( FATAL_ERROR "INVALID SOLVER OS COMBINATION" )
endif()

# INCLUDE THE CUSTOM LINKING DIRECTORIES IF DEFINED
if(NOT "${LIBDIR}" STREQUAL "DEFAULT")
foreach(libir ${LIBDIR})
link_directories(${libdir})
endforeach(libdir)
endif()
##----------------------------------------------------------------------------------------------------------------------


# CREATE THE TARGET (executable or library)
if(${MYTARGET} STREQUAL "exe")
add_executable(${EXEC} ${SOURCE_FILES})
elseif(${MYTARGET} STREQUAL "lib")
message(MAKING_LIBRARY)
add_library(${EXEC} ${SOURCE_FILES})
elseif(${MYTARGET} STREQUAL "both")
add_library(${EXEC} ${SOURCE_FILES})
add_executable(${EXEC} ${SOURCE_FILES})
elseif(${MYTARGET} STREQUAL "test")
LIST(REMOVE_ITEM SOURCE_FILES main.cpp)
add_executable(${EXEC} test.cpp ${SOURCE_FILES})
message(MAKING_TEST)
else()
message( FATAL_ERROR "INVALID TARGET")
endif()
##----------------------------------------------------------------------------------------------------------------------



# LINK THE DESIRED LIBRARIES (The order of linking matters! DO NOT CHANGE IT!)
if(${mySystem} STREQUAL "LINUX" AND ${SOLVER} STREQUAL "gurobi")
if("${MYLIBRARIES}" STREQUAL "DEFAULT")
target_link_libraries(${EXEC} m gurobi_c++ gurobi70)                              #### GUROBI MAJOR VERSION (GUROBI 1/6)  ####
else()
foreach(mylib ${MYLIBRARIES})
target_link_libraries(${EXEC} m gurobi_c++ gurobi70 ${mylib})                     #### GUROBI MAJOR VERSION (GUROBI 2/6)  ####
endforeach(mylib)
endif()
elseif(${mySystem} STREQUAL "WINDOWS" AND ${SOLVER} STREQUAL "gurobi")
if(${CMAKE_BUILD_TYPE} STREQUAL "Release")
target_link_libraries(${EXEC} gurobi_c++md2015.lib)                               #### VISUAL STUDIO VERSION (GUROBI 3/6) ####
else() #Debug mode by default
target_link_libraries(${EXEC} gurobi_c++mdd2015.lib)                              #### VISUAL STUDIO VERSION (GUROBI 4/6) ####
endif()
if("${MYLIBRARIES}" STREQUAL "DEFAULT")
target_link_libraries(${EXEC} gurobi70.lib)                                       #### GUROBI MAJOR VERSION (GUROBI 5/6)  ####
else()
foreach(mylib ${MYLIBRARIES})
target_link_libraries(${EXEC} gurobi70.lib  ${mylib})                             #### GUROBI MAJOR VERSION (GUROBI 6/6)  ####
endforeach(mylib)
endif()
elseif(${mySystem} STREQUAL "LINUX" AND ${SOLVER} STREQUAL "cplex")
if("${MYLIBRARIES}" STREQUAL "DEFAULT")
target_link_libraries(${EXEC} concert ilocplex cplex m pthread)
else()
foreach(mylib ${MYLIBRARIES})
target_link_libraries(${EXEC} concert ilocplex cplex m pthread ${mylib})
endforeach(mylib)
endif()
elseif(${mySystem} STREQUAL "WINDOWS" AND ${SOLVER} STREQUAL "cplex")
if("${MYLIBRARIES}" STREQUAL "DEFAULT")
target_link_libraries(${EXEC} concert.lib ilocplex.lib cplex1271.lib)              #### CPLEX MAJOR VERSION (CPLEX 3/4)  ####
else()
foreach(mylib ${MYLIBRARIES})
target_link_libraries(${EXEC} concert.lib ilocplex.lib cplex1271.lib ${mylib})     #### CPLEX MAJOR VERSION (CPLEX 4/4)  ####
endforeach(mylib)
endif()
else()
message( FATAL_ERROR "INVALID SOLVER OS COMBINATION" )
endif()


## LINK BOOST LIBRARIES
if(${ADD_BOOST} STREQUAL "yes")
target_link_libraries (${EXEC} ${Boost_LIBRARIES})
endif()

# LINK CONAN PACKAGE MANAGER
if(${ADD_CONAN} STREQUAL "yes")
target_link_libraries(${EXEC} ${CONAN_LIBS})
endif()

##----------------------------------------------------------------------------------------------------------------------

########################################################################################################################
########################################################################################################################