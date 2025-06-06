# -*- coding: utf-8 -*- #
# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command for deleting organization security policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.org_security_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.org_security_policies import flags
from googlecloudsdk.command_lib.compute.org_security_policies import org_security_policies_utils
import six


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Delete(base.DeleteCommand):
  """Delete a Compute Engine organization security policy.

  *{command}* is used to delete organization security policies. An organization
  security policy is a set of rules that controls access to various resources.
  """

  ORG_SECURITY_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ORG_SECURITY_POLICY_ARG = flags.OrgSecurityPolicyArgument(
        required=True, operation='delete')
    cls.ORG_SECURITY_POLICY_ARG.AddArgument(parser, operation_type='delete')
    parser.add_argument(
        '--organization',
        help=('Organization in which the organization security policy is to be'
              ' deleted. Must be set if SECURITY_POLICY is short name.'))
    parser.display_info.AddCacheUpdater(flags.OrgSecurityPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.ORG_SECURITY_POLICY_ARG.ResolveAsResource(
        args, holder.resources, with_project=False)
    org_security_policy = client.OrgSecurityPolicy(
        ref=ref,
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower())
    sp_id = org_security_policies_utils.GetSecurityPolicyId(
        org_security_policy, ref.Name(), organization=args.organization)
    return org_security_policy.Delete(sp_id=sp_id, only_generate_request=False)


Delete.detailed_help = {
    'EXAMPLES':
        """\
    To delete an organization security policy with ID "123456789", run:

      $ {command} delete 123456789
    """,
}
