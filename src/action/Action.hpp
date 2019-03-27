#pragma once

#include "mesh/SharedPointer.hpp"
#include "mapping/Mapping.hpp"

#include "someFancyHEadder.hpp"

namespace precice
{
namespace action
{

/**
 * @brief Abstract base class for configurable actions on data and/or meshes.
 *
 * Actions are executed on call of precice::SolverInterface::initialize(),
 * precice::SolverInterface::initializeData(), and precice::SolverInterface::advance(). They can change meshes and in particular
 * data values.
 */
class Action
{
public:
  /// Defines the time and place of application of the action.
  enum Timing {
    ALWAYS_PRIOR,             // Everytime, before advancing cpl scheme
    ALWAYS_POST,              // Everytime, after advancing cpl scheme
    ON_EXCHANGE_PRIOR,        // On data exchange, before advancing cpl scheme
    ON_EXCHANGE_POST,         // On data exchange, after advancing cpl scheme
    ON_TIMESTEP_COMPLETE_POST // On advancing to next dt, after adv. cpl scheme
  };

  Action(
      Timing               timing,
      const mesh::PtrMesh &mesh,
      mapping::Mapping::MeshRequirement requirement)
      : _timing(timing),
        _mesh(mesh),
        _meshRequirement(requirement)
  {
  }

  Action(
      Timing               timing,
      const mesh::PtrMesh &mesh
      )
      : _timing(timing),
        _mesh(mesh)
  {
  }

  /// Destructor, empty.
  virtual ~Action() {}

  /**
    * @brief Performs the action, to be overwritten by subclasses.
    *
    * @param[in] time the current total simulation time. 
    * @param[in] dt Length of last local timestep computed.
    * @param[in] computedPartFullDt Sum of all local timesteps of current global timestep.
    * @param fullDt[in] Current global timestep length.
    */
  virtual void performAction(
      double time,
      double dt,
      double computedPartFullDt,
      double fullDt) = 0;

  /// Returns the timing of the action.
  Timing getTiming() const
  {
    return _timing;
  }

  /// Returns the mesh carrying the data used in the action.
  const mesh::PtrMesh &getMesh() const
  {
    return _mesh;
  }

  /// Returns the mesh requirement of this action
  mapping::Mapping::MeshRequirement getMeshRequirement() const
  {
    return _meshRequirement;
  }

private:
  /// Determines when the action will be executed.
  Timing _timing;

  /// Mesh carrying the data used in the action.
  mesh::PtrMesh _mesh;

  /// The mesh requirements for the mesh
  mapping::Mapping::MeshRequirement _meshRequirement = mapping::Mapping::MeshRequirement::UNDEFINED;
};

} // namespace action
} // namespace precice
