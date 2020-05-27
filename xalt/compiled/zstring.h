#ifndef ZSTRING_H
#define ZSTRING_H

#include <string>
#include <zlib.h>
std::string  compress_string(  const std::string& str, int compressionlevel = Z_BEST_COMPRESSION);
std::string  decompress_string(const std::string& str);

#endif //ZSTRING_H
