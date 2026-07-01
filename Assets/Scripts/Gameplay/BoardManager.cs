using UnityEngine;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Manages the game board: 3 location slots and 2 deployment zones.
    /// Mirrors the Python engine/board.py Board class.
    /// </summary>
    public class BoardManager : MonoBehaviour
    {
        public const int MaxRowCapacity = 4;
        public const int LocationCount = 3;

        [Header("Locations")]
        public List<LocationSlot> locations = new List<LocationSlot>();

        [Header("Deployment Zones")]
        public List<BoardAlly> fpDeployment = new List<BoardAlly>();
        public List<BoardAlly> shadowDeployment = new List<BoardAlly>();

        // --- Initialization ---

        public void Initialize()
        {
            locations.Clear();
            for (int i = 0; i < LocationCount; i++)
                locations.Add(new LocationSlot { index = i });
        }

        // --- Location Access ---

        public LocationSlot GetLocation(int index)
        {
            if (index >= 0 && index < locations.Count)
                return locations[index];
            return null;
        }

        // --- Card Play ---

        /// <summary>
        /// Play a location card into a slot. Returns false if slot occupied.
        /// </summary>
        public bool PlayLocation(CardData card, string player, int slotIndex)
        {
            LocationSlot loc = GetLocation(slotIndex);
            if (loc == null || !loc.IsEmpty)
                return false;
            loc.locationCard = card;
            loc.currentDefense = card.defense;
            loc.controller = player;
            return true;
        }

        /// <summary>
        /// Deploy an ally to the player's deployment zone.
        /// </summary>
        public bool DeployAlly(BoardAlly ally, string player)
        {
            List<BoardAlly> zone = player == "fp" ? fpDeployment : shadowDeployment;
            zone.Add(ally);
            return true;
        }

        // --- Movement ---

        /// <summary>
        /// Move an ally from deployment (or another location) to a location row.
        /// </summary>
        public bool MoveAllyToLocation(BoardAlly ally, string player, int locationIndex, string row = "front")
        {
            // Remove from current position
            List<BoardAlly> zone = player == "fp" ? fpDeployment : shadowDeployment;
            if (zone.Contains(ally))
                zone.Remove(ally);
            else
            {
                bool found = false;
                foreach (var loc in locations)
                {
                    if (loc.RemoveAlly(ally, player))
                    {
                        found = true;
                        break;
                    }
                }
                if (!found)
                    return false;
            }

            // Add to target location
            LocationSlot target = GetLocation(locationIndex);
            if (target == null)
                return false;
            return target.AddAlly(ally, player, row);
        }

        /// <summary>
        /// Move an ally between two location slots.
        /// </summary>
        public bool MoveAllyBetweenLocations(BoardAlly ally, string player,
            int fromIndex, int toIndex, string toRow = "front")
        {
            LocationSlot fromLoc = GetLocation(fromIndex);
            LocationSlot toLoc = GetLocation(toIndex);
            if (fromLoc == null || toLoc == null)
                return false;
            if (!fromLoc.RemoveAlly(ally, player))
                return false;
            return toLoc.AddAlly(ally, player, toRow);
        }

        /// <summary>
        /// Move an ally between front and back line at the same location.
        /// </summary>
        public bool MoveAllyBetweenRows(BoardAlly ally, string player,
            int locationIndex, string targetRow)
        {
            LocationSlot loc = GetLocation(locationIndex);
            if (loc == null)
                return false;
            string currentRow = loc.FindAllyRow(ally, player);
            if (currentRow == null || currentRow == targetRow)
                return false;
            if (!loc.RemoveAlly(ally, player))
                return false;
            return loc.AddAlly(ally, player, targetRow);
        }

        // --- Search ---

        /// <summary>
        /// Find an ally's location index. Returns -1 for deployment, null if not found.
        /// </summary>
        public int? FindAllyLocation(BoardAlly ally, string player)
        {
            List<BoardAlly> zone = player == "fp" ? fpDeployment : shadowDeployment;
            if (zone.Contains(ally))
                return -1;
            for (int i = 0; i < locations.Count; i++)
            {
                if (locations[i].GetAllies(player).Contains(ally))
                    return i;
            }
            return null;
        }

        /// <summary>
        /// Get all allies on the board for a player (deployment + locations).
        /// </summary>
        public List<BoardAlly> GetAllAllies(string player)
        {
            List<BoardAlly> zone = player == "fp" ? fpDeployment : shadowDeployment;
            var result = new List<BoardAlly>(zone);
            foreach (var loc in locations)
                result.AddRange(loc.GetAllies(player));
            return result;
        }

        /// <summary>
        /// Remove an ally from anywhere on the board. Returns true if found.
        /// </summary>
        public bool RemoveAlly(BoardAlly ally, string player)
        {
            List<BoardAlly> zone = player == "fp" ? fpDeployment : shadowDeployment;
            if (zone.Contains(ally))
            {
                zone.Remove(ally);
                return true;
            }
            foreach (var loc in locations)
            {
                if (loc.RemoveAlly(ally, player))
                    return true;
            }
            return false;
        }

        // --- Attack Targets ---

        /// <summary>
        /// Get valid attack targets for an attacker at its location.
        /// TODO: Implement full targeting logic in game loop phase.
        /// </summary>
        public List<BoardAlly> GetValidAttackTargets(BoardAlly attacker, string attackerPlayer, int locationIndex)
        {
            // TODO: Implement based on Python LocationSlot.valid_attack_targets
            return new List<BoardAlly>();
        }

        // --- Cleanup ---

        /// <summary>
        /// Remove dead allies from all locations and deployment zones.
        /// Returns them so they can be placed in discard.
        /// </summary>
        public List<BoardAlly> RemoveDeadAllies(string player)
        {
            var dead = new List<BoardAlly>();
            foreach (var loc in locations)
            {
                RemoveDeadFromLine(loc.GetFrontLine(player), dead);
                RemoveDeadFromLine(loc.GetBackLine(player), dead);
            }
            List<BoardAlly> zone = player == "fp" ? fpDeployment : shadowDeployment;
            RemoveDeadFromLine(zone, dead);
            return dead;
        }

        private static void RemoveDeadFromLine(List<BoardAlly> line, List<BoardAlly> dead)
        {
            for (int i = line.Count - 1; i >= 0; i--)
            {
                if (!line[i].IsAlive)
                {
                    dead.Add(line[i]);
                    line.RemoveAt(i);
                }
            }
        }
    }
}
