#pragma once

#include "BaseCouplingScheme.hpp"
#include "logging/Logger.hpp"

// Forward declaration to friend the boost test struct
namespace CplSchemeTests {
namespace SerialImplicitCouplingSchemeTests {
struct testExtrapolateData;
}
} // namespace CplSchemeTests

namespace precice {
namespace cplscheme {

/**
 * @brief Coupling scheme for serial coupling, i.e. staggered execution of two coupled participants
 *
 * For more information, look into Benjamin's thesis, Section 3.5. 
 * https://mediatum.ub.tum.de/doc/1320661/document.pdf
 */
class SerialCouplingScheme : public BaseCouplingScheme {
public:
  /**
 * @brief Constructor.
 *
 * @param[in] maxTime Simulation time limit, or UNDEFINED_TIME.
 * @param[in] maxTimeWindows Simulation time windows limit, or UNDEFINED_TIMEWINDOWS.
 * @param[in] timeWindowSize Simulation time window size.
 * @param[in] validDigits TODO
 * @param[in] firstParticipant Name of participant starting simulation.
 * @param[in] secondParticipant Name of second participant in coupling.
 * @param[in] localParticipant Name of participant using this coupling scheme.
 * @param[in] m2n Communication object for com. between participants. TODO?
 * TODO add dtMethod, cplMode, maxIterations
 */
  SerialCouplingScheme(
      double                        maxTime,
      int                           maxTimeWindows,
      double                        timeWindowSize,
      int                           validDigits,
      const std::string &           firstParticipant,
      const std::string &           secondParticipant,
      const std::string &           localParticipant,
      m2n::PtrM2N                   m2n,
      constants::TimesteppingMethod dtMethod,
      CouplingMode                  cplMode,
      int                           maxIterations = 1);

  /**
   * @brief TODO
   *
   * @param[in] startTime TODO
   * @param[in] startTimeWindow TODO
   */
  virtual void initialize(double startTime, int startTimeWindow);

  virtual void initializeData();

  virtual void advance();

  logging::Logger _log{"cplschemes::SerialCouplingSchemes"};

  friend struct CplSchemeTests::SerialImplicitCouplingSchemeTests::testExtrapolateData; // For whitebox tests

private:
  virtual void explicitAdvance();

  virtual void implicitAdvance();
};

} // namespace cplscheme
} // namespace precice
