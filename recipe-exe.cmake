function(_recipe_ScratchEverywhere_system)
  find_program(SE_SYSTEM_EXE NAMES scratch-everywhere scratch-pc)
  if(SE_SYSTEM_EXE AND NOT TARGET ScratchEverywhere)
    add_executable(ScratchEverywhere IMPORTED GLOBAL)
    set_target_properties(ScratchEverywhere PROPERTIES IMPORTED_LOCATION "${SE_SYSTEM_EXE}")
  endif()
endfunction()

function(_recipe_ScratchEverywhere_source)
  set(SE_REF "1.3")
  if(CL_REQ_VERSION)
    set(SE_REF "${CL_REQ_VERSION}")
  endif()
  cl_set_version("${SE_REF}")

  cl_import_source(
    NAME ScratchEverywhere
    REPO https://github.com/ScratchEverywhere/ScratchEverywhere.git
    REF ${SE_REF}
  )

  if(TARGET scratch-everywhere)
    add_executable(deps::ScratchEverywhere ALIAS scratch-everywhere)
  endif()
endfunction()

function(_recipe_ScratchEverywhere_latest)
  set(SE_REF "1.3")
  if(CL_REQ_VERSION)
    set(SE_REF "${CL_REQ_VERSION}")
  endif()
  cl_set_version("${SE_REF}")
endfunction()

function(_recipe_ScratchEverywhere_install PREFIX)
  file(GLOB_RECURSE SE_BUILT_EXE
    "${CL_SOURCE_BUILD_DIR}/scratch-pc"
    "${CL_SOURCE_BUILD_DIR}/scratch-pc.exe"
  )
  if(NOT SE_BUILT_EXE)
    message(FATAL_ERROR "now how tf did this happen")
  endif()
  list(GET SE_BUILT_EXE 0 SE_BUILT_EXE)
  cl_install_files("${SE_BUILT_EXE}" DESTINATION bin)
endfunction()
