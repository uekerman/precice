#pragma once

#include "BaseCouplingScheme.hpp"
#include "logging/Logger.hpp"

namespace precice {
namespace cplscheme {

/**
 * @brief TODO
 */
class MultiCouplingScheme : public BaseCouplingScheme {
public:
  /**
 * @brief Constructor.
 *
 * @param[in] maxTime Simulation time limit, or UNDEFINED_TIME.
 * @param[in] maxTimeWindows Simulation time windows limit, or UNDEFINED_TIMEWINDOWS.
 * @param[in] timeWindowSize Simulation time window size.
 * @param[in] validDigits TODO
 * @param[in] localParticipant Name of participant using this coupling scheme.
 * @param[in] m2n Communication object for com. between participants. TODO?
 * TODO add dtMethod, maxIterations
 */
  MultiCouplingScheme(
      double                        maxTime,
      int                           maxTimeWindows,
      double                        timeWindowSize,
      int                           validDigits,
      const std::string &           localParticipant,
      std::vector<m2n::PtrM2N>      m2n,
      constants::TimesteppingMethod dtMethod,
      int                           maxIterations = 1);

  logging::Logger _log{"cplscheme::MultiCouplingScheme"};

  /**
 * @brief TODO
 *
 * @param[in] startTime TODO
 * @param[in] startTimeWindow TODO
 */
  virtual void initialize(double startTime, int startTimeWindow);

  virtual void initializeData();

  virtual void advance();

  /// Adds data to be sent on data exchange and possibly be modified during coupling iterations.
  void addDataToSend(
      mesh::PtrData data,
      mesh::PtrMesh mesh,
      bool          initialize,
      int           index);

  /// Adds data to be received on data exchange.
  void addDataToReceive(
      mesh::PtrData data,
      mesh::PtrMesh mesh,
      bool          initialize,
      int           index);

protected:
  /// merges send and receive data into one map (for parallel acceleration)
  virtual void mergeData();

private:
  void          sendData();
  void          receiveData();
  void          setupConvergenceMeasures();
  CouplingData *getData(int dataID);

  /// Communication device to the other coupling participant.
  std::vector<m2n::PtrM2N> _communications;

  /// Map from data ID -> all data (receive and send) with that ID
  DataMap _allData;

  std::vector<DataMap> _receiveDataVector;
  std::vector<DataMap> _sendDataVector;
};

} // namespace cplscheme
} // namespace precice
