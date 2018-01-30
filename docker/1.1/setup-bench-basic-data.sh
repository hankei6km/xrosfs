#!/bin/sh

set -e

setup_access () {
    ACCESS_PATH="${MNT_BASE_PATH}/access"
    mkdir -p ${ACCESS_PATH}
    touch "${ACCESS_PATH}/test.txt"
    touch "${ACCESS_PATH}/test_x.txt"
    chmod u+x "${ACCESS_PATH}/test_x.txt"
}

setup_chmod () {
    CHMOD_PATH="${MNT_BASE_PATH}/chmod"
    mkdir -p ${CHMOD_PATH}
    touch "${CHMOD_PATH}/test.txt"
}

setup_chown () {
    CHOWN_PATH="${MNT_BASE_PATH}/chown"
    mkdir -p ${CHOWN_PATH}
    touch "${CHOWN_PATH}/test.txt"
    chmod 777 "${CHOWN_PATH}/test.txt"
}

setup_getattr () {
    GETATTR_PATH="${MNT_BASE_PATH}/getattr"
    mkdir -p ${GETATTR_PATH}
    echo 'test' >  "${GETATTR_PATH}/test.txt"
}

setup_link () {
    LINK_DIR="${MNT_BASE_PATH}/link"
    mkdir -p ${LINK_DIR}
    echo 'target file' > ${LINK_DIR}/file_target
}

setup_mkdir () {
    MKDIR="${MNT_BASE_PATH}/mkdir"
    mkdir -p ${MKDIR}/dir_exist
}

setup_read_write () {
    READ_WRITE_PATH="${MNT_BASE_PATH}/read_write"
    mkdir -p ${READ_WRITE_PATH}
    touch "${READ_WRITE_PATH}/test.txt"
}

setup_readdir () {
    READ_PATH="${MNT_BASE_PATH}/readdir"
    mkdir -p ${READ_PATH}
    touch "${READ_PATH}/test1.txt"
    touch "${READ_PATH}/test2.txt"
}

setup_readlink () {
    READLINK_PATH="${MNT_BASE_PATH}/readlink"
    mkdir -p ${READLINK_PATH}/tgt
    echo 'target file' >  "${READLINK_PATH}/tgt/target.txt"
    # always overwrite...
    echo 'outer target in container' >  "/export/outer_target.txt"

    # pushd "${READLINK_PATH}"
    cd "${READLINK_PATH}"
    ln -s "tgt/target.txt"  "${READLINK_PATH}"/link_rel.txt
    ln -s "${READLINK_PATH}/tgt/target.txt" "${READLINK_PATH}"/link_abs.txt
    ln -s "../../outer_target.txt" link_outer.txt
    # popd
    cd - > /dev/null
}

setup_rmdir () {
    RMDIR_PATH="${MNT_BASE_PATH}/rmdir"
    mkdir -p ${RMDIR_PATH}/dir_empty

    mkdir -p ${RMDIR_PATH}/dir_normal
    touch ${RMDIR_PATH}/dir_normal/test.txt
}

setup_statfs () {
    STATFS_PATH="${MNT_BASE_PATH}/statfs"
    mkdir -p ${STATFS_PATH}
}

setup_symlink () {
    SYMLINK_DIR="${MNT_BASE_PATH}/symlink"
    mkdir -p ${SYMLINK_DIR}/dir_target
    touch ${SYMLINK_DIR}/dir_target/test1.txt
    touch ${SYMLINK_DIR}/dir_target/test2.txt
    echo 'target file' > ${SYMLINK_DIR}/file_target
}

setup_rename () {
    RENAME_PATH="${MNT_BASE_PATH}/rename"
    mkdir -p ${RENAME_PATH}/old
    touch "${RENAME_PATH}/test_old.txt"
    touch "${RENAME_PATH}/old/test.txt"
}

setup_unlink () {
    UNLINK_PATH="${MNT_BASE_PATH}/unlink"
    mkdir -p ${UNLINK_PATH}
    touch "${UNLINK_PATH}/test.txt"
}

setup_truncate () {
    TRUNCATE_PATH="${MNT_BASE_PATH}/truncate"
    mkdir -p ${TRUNCATE_PATH}
    touch "${TRUNCATE_PATH}/test.txt"
}

setup_utimens () {
    UTIMENS_PATH="${MNT_BASE_PATH}/utimens"
    mkdir -p ${UTIMENS_PATH}
    echo "test" > "${UTIMENS_PATH}/test.txt"
    touch -a -t "201701020304.05" "${UTIMENS_PATH}/test.txt"
    touch -m -t "201706070809.10" "${UTIMENS_PATH}/test.txt"
}


setup_all () {
  setup_access
  setup_chmod
  setup_chown
  setup_getattr
  setup_link
  setup_read_write
  setup_mkdir
  setup_readdir
  setup_readlink
  setup_rmdir
  setup_statfs
  setup_symlink
  setup_rename
  setup_unlink
  setup_truncate
  setup_utimens
}


MNT_BASE_PATH='/export/sshfs'
setup_all
MNT_BASE_PATH='/export/xrosfs'
setup_all
