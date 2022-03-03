// Copyright (c) 2011-present, Facebook, Inc.  All rights reserved.
//  This source code is licensed under both the GPLv2 (found in the
//  COPYING file in the root directory) and Apache 2.0 License
//  (found in the LICENSE.Apache file in the root directory).

#include <cstdio>
#include <string>

#include <iostream>
#include <chrono>
#include <thread>

#include "rocksdb/db.h"
#include "rocksdb/slice.h"
#include "rocksdb/options.h"

#include "db/db_impl/db_impl.h"
#include "util/cast_util.h"

#include <thread>
#include <iostream>
#include <vector>

using namespace ROCKSDB_NAMESPACE;

#if defined(OS_WIN)
std::string kDBPath = "C:\\Windows\\TEMP\\rocksdb_my_own_example";
#else
std::string kDBPath = "/tmp/rocksdb_my_own_example";
#endif

void action(DB* db, int runs, int id) {
  for (int i = 0; i < runs; i++) {
    //Status s = db -> Put(WriteOptions(), "1", std::to_string(i + runs * id));
    Status s = db -> Put(WriteOptions(), std::to_string(i + runs * id), "1");
    assert(s.ok());
  }
}

int main() {
  DB* db;
  Options options;
  // Optimize RocksDB. This is the easiest way to get RocksDB to perform well
  options.IncreaseParallelism(2);
  options.OptimizeLevelStyleCompaction();
  // create the DB if it's not already present
  options.create_if_missing = true;
  options.statistics = rocksdb::CreateDBStatistics(); // ADDED BY ME
  options.statistics -> set_stats_level(kAll);

  std::cout << "InstrMuLocks b/ open: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;

  // open DB
  Status s = DB::Open(options, kDBPath, &db);

  std::cout << "InstrMuLocks a/ open: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;
  assert(s.ok());

  std::cout << "InstrMuLocks a/ assert: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;

  int nthreads = 16;
  std::cout << "Threads: " << nthreads << std::endl;

  int runs = 100000 / nthreads;

  std::vector<std::thread> threads(nthreads);

  for (int i = 0; i < nthreads; i++) {
    threads[i] = std::thread(action, db, runs, i);
  }

  for (auto& th : threads) {
    th.join();
  }

  /*// atomically apply a set of updates
  for (int i = 0; i < runs; ++i) {
    {
      //WriteBatch batch;
      //batch.Delete(std::to_string(i - 1));
      //batch.Put(std::to_string(i), value);
      //s = db->Write(WriteOptions(), &batch);
      s = db -> Put(WriteOptions(), std::to_string(1), std::to_string(i));
      assert(s.ok());
    }
  }*/

  std::cout << "InstrMuLocks b/ cleanup: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;

  // trying to enforce writing updated stats to LOG file
  //DBImpl* dbi = static_cast_with_check<DBImpl>(db);
  //dbi -> DumpStats();
  
  delete db;
  DestroyDB(kDBPath, options);

  std::cout << "InstrMuLocks a/ cleanup: " << options.statistics->getTickerCount(INSTRUMENTED_MUTEX_LOCK) << std::endl;
  //std::cout << "instrumented_mutex_counter: " << mutex_counter << std::endl;

  return 0;
}
