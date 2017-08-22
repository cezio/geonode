import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { getResponseData } from '../../../utils';
import AverageResponseTime from '../../molecules/average-response-time';
import MaxResponseTime from '../../molecules/max-response-time';
import TotalRequests from '../../molecules/total-requests';
import styles from './styles';
import actions from './actions';


const mapStateToProps = (state) => ({
  from: state.interval.from,
  interval: state.interval.interval,
  response: state.geonodeAverageResponse.response,
  to: state.interval.to,
});


@connect(mapStateToProps, actions)
class GeonodeData extends React.Component {
  static propTypes = {
    from: PropTypes.object,
    get: PropTypes.func.isRequired,
    interval: PropTypes.number,
    reset: PropTypes.func.isRequired,
    response: PropTypes.object,
    to: PropTypes.object,
  }

  constructor(props) {
    super(props);
    this.get = (
      from = this.props.from,
      to = this.props.to,
      interval = this.props.interval,
    ) => {
      this.props.get(from, to, interval);
    };
  }

  componentWillMount() {
    this.get();
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps) {
      if (nextProps.from && nextProps.from !== this.props.from) {
        this.get(nextProps.from, nextProps.to, nextProps.interval);
      }
    }
  }

  componentWillUnmount() {
    this.props.reset();
  }

  render() {
    let averageResponseTime = 0;
    let maxResponseTime = 0;
    let totalRequests = 0;
    [
      averageResponseTime,
      maxResponseTime,
      totalRequests,
    ] = getResponseData(this.props.response);
    return (
      <div style={styles.content}>
        <h5>Geonode Data Overview</h5>
        <div style={styles.geonode}>
          <AverageResponseTime time={averageResponseTime} />
          <MaxResponseTime time={maxResponseTime} />
        </div>
        <TotalRequests requests={totalRequests} />
      </div>
    );
  }
}


export default GeonodeData;