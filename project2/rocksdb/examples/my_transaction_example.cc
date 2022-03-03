// Copyright (c) 2011-present, Facebook, Inc.  All rights reserved.
//  This source code is licensed under both the GPLv2 (found in the
//  COPYING file in the root directory) and Apache 2.0 License
//  (found in the LICENSE.Apache file in the root directory).

#ifndef ROCKSDB_LITE

#include <iostream>

#include "rocksdb/db.h"
#include "rocksdb/options.h"
#include "rocksdb/slice.h"
#include "rocksdb/utilities/transaction.h"
#include "rocksdb/utilities/transaction_db.h"

#include <thread>
#include <iostream>
#include <vector>

using namespace ROCKSDB_NAMESPACE;

#if defined(OS_WIN)
std::string kDBPath = "C:\\Windows\\TEMP\\rocksdb_my_transaction_example";
#else
std::string kDBPath = "/tmp/rocksdb_my_transaction_example";
#endif

void action(TransactionDB* txn_db, WriteOptions write_options, int runs, int id) {
  Status s;
  for (int i = 0; i < runs; i++) {
    // Start a transaction
    Transaction* txn = txn_db->BeginTransaction(write_options);
    assert(txn);

    // Write a key in this transaction
    s = txn->Put("a", std::to_string(i + runs * id ));
    //s = txn -> Put(std::to_string(i + runs * id ), "b");
    assert(s.ok());

    // Commit transaction
    s = txn->Commit();
    assert(s.ok());
    delete txn;
  }
}

int main() {
  // open DB
  Options options;
  TransactionDBOptions txn_db_options;
  options.create_if_missing = true;
  // Optimize RocksDB. This is the easiest way to get RocksDB to perform well
  options.IncreaseParallelism(2);
  options.OptimizeLevelStyleCompaction();

  options.statistics = rocksdb::CreateDBStatistics(); // ADDED BY ME
  options.statistics -> set_stats_level(kAll);

  TransactionDB* txn_db;

  Status s = TransactionDB::Open(options, txn_db_options, kDBPath, &txn_db);
  assert(s.ok());

  WriteOptions write_options;
  ReadOptions read_options;
  TransactionOptions txn_options;
  std::string value;

  ////////////////////////////////////////////////////////
  //
  // Simple Transaction Example ("Read Committed")
  //
  ////////////////////////////////////////////////////////

  std::cout << "InstrMuLocks b/ trans: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;

  // Start a transaction
  /*Transaction* txn = txn_db->BeginTransaction(write_options);
  assert(txn);

  // Read a key in this transaction
  s = txn->Get(read_options, "abc", &value);
  assert(s.IsNotFound());
  

  // Write a key in this transaction
  s = txn->Put("a", "b");
  assert(s.ok());

  // Value for key "xyz" has been committed, can be read in txn.
  s = txn->Get(read_options, "a", &value);
  assert(s.ok());

  // Commit transaction
  s = txn->Commit();
  assert(s.ok());
  delete txn;
  */

  int nthreads = 16;
  std::cout << "threads: " << nthreads << std::endl;
  int runs = 100000 / nthreads;

  std::vector<std::thread> threads(nthreads);

  for (int i = 0; i < nthreads; i++) {
    threads[i] = std::thread(action, txn_db, write_options, runs, i);
  }

  for (auto& th : threads) {
    th.join();
  }


  std::cout << "InstrMuLocks a/ trans: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;
  //std::string num;
  //txn_db->GetProperty("rocksdb.estimate-num-keys", &num);
  //std::cout << "keys: " << num << std::endl;

  // Cleanup
  delete txn_db;
  DestroyDB(kDBPath, options);

  std::cout << "InstrMuLocks a/ cleanup: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;

  return 0;
}

#endif  // ROCKSDB_LITE
